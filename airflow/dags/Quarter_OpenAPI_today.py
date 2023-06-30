import io
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from google.cloud import bigquery, storage
from pytz import timezone

from plugins import slack

DAG_ID = "Quarter_OpenAPI_today"
dag = DAG(
    DAG_ID,
    schedule_interval="*/15 * * * *",
    start_date=datetime(2023, 6, 25),
    catchup=False,
    default_args={
        "on_failure_callback": slack.on_failure_callback,
    },
)


def extract_data_OpenAPI(**context):
    OpenAPI_URL = context["params"]["OpenAPI_URL"]
    OpenAPI_KEY = context["params"]["OpenAPI_KEY"]

    result_df = pd.DataFrame(
        columns=[
            "desertionNo",
            "filename",
            "happenDt",
            "happenPlace",
            "kindCd",
            "colorCd",
            "age",
            "weight",
            "noticeNo",
            "noticeSdt",
            "noticeEdt",
            "popfile",
            "processState",
            "sexCd",
            "neuterYn",
            "specialMark",
            "careNm",
            "careTel",
            "careAddr",
            "orgNm",
            "chargeNm",
            "officetel",
            "noticeComment",
        ]
    )

    datetime_kst = datetime.now(timezone("Asia/Seoul"))
    today_HM = datetime_kst.strftime("%Y%m%d-%H%M")
    today = datetime_kst.strftime("%Y%m%d")
    params = {
        "serviceKey": OpenAPI_KEY,
        "bgnde": today,
        "endde": today,
        "numOfRows": "1000",
        "_type": "json",
    }

    MAX_RETRIES = 10
    for _ in range(MAX_RETRIES):
        try:
            my_response = requests.get(OpenAPI_URL, params=params, timeout=5)

            if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in my_response.text:
                raise Exception(
                    "공공데이터 OpenAPI Server error: SERVICE_KEY_IS_NOT_REGISTERED_ERROR"
                )
            else:
                df_today_data = pd.DataFrame(
                    json.loads(my_response.text)["response"]["body"]["items"]["item"]
                )  # daily data json -> df
                result_df = pd.concat([result_df, df_today_data], ignore_index=True)
                print(today_HM, "성공 데이터 :", result_df.shape[0])
                break
        except Exception as e:
            if "item" in e:
                print(today_HM + "기준", "등록된 유기동물 데이터가 없습니다.")
                break
            print(today_HM, "등록되지 않은 error :", e)
    else:
        raise AirflowException("10회 이상 추출 실패, OpenAPI 서버 문제로 추출 중단")

    SAVE_NAME = "strayanimal_today_data_" + today_HM + ".csv"

    LOCAL_PATH_NAME = os.path.join(
        os.environ["AIRFLOW_HOME"], "data", "strayanimal_today_data", SAVE_NAME
    )
    result_df.to_csv(LOCAL_PATH_NAME, encoding="utf-8-sig")

    return SAVE_NAME, LOCAL_PATH_NAME


def upload_data_GCS(**context):
    SAVE_NAME, LOCAL_PATH_NAME = context["ti"].xcom_pull(
        task_ids="extract_data_OpenAPI"
    )

    # LOCAL_PATH_NAME = 'strayanimal_today_data_20230625-0000.csv'
    # SAVE_NAME[:-9]로 사용
    SAVE_NAME = SAVE_NAME[:-9]

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.environ["AIRFLOW_HOME"], "keys", "strayanimal-bucket.json"
    )

    bucket_name = "strayanimal-bucket"  # bucket 이름
    BUCKET_PATH = "raw-data/strayanimal-today_data/"  # bucket 내부 위치
    destination_blob_name = BUCKET_PATH + SAVE_NAME  # 업로드 위치 + 업로드될 파일 이름

    # GCP Storage에 client 연결
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 파일 업로드
    blob.upload_from_filename(LOCAL_PATH_NAME, content_type="text/csv")

    print("Cloud Storage 적재 성공")


def read_data_from_storage(**context):
    try:
        bucket_name = context["params"]["bucket_name"]
        today = datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d")
        file_name = f"raw-data/strayanimal-today_data/strayanimal_today_data_{today}"

        storage_client = storage.Client()
        blob = storage_client.get_bucket(bucket_name).get_blob(file_name)
        csv_data = blob.download_as_text().splitlines()
        df = pd.read_csv(io.StringIO("\n".join(csv_data)))

        print(f"{file_name} 읽어오기 성공")

        return df

    except Exception as e:
        print("read_data_from_storage - 오류 발생 : ", e)
        raise AirflowException(f"오류 발생. {e}")


def transform_data(**context):
    df = context["ti"].xcom_pull(task_ids="read_data_from_storage")

    if len(df) > 0:
        df = df.drop(df.columns[df.columns.str.contains("unnamed", case=False)], axis=1)
        if "noticeComment" not in df.columns:
            df["noticeComment"] = np.nan

        df["desertionNo"] = df["desertionNo"].astype(int)
        df["happenDt"] = pd.to_datetime(df["happenDt"], format="%Y%m%d")
        df["noticeEdt"] = pd.to_datetime(df["noticeEdt"], format="%Y%m%d")
        df["noticeSdt"] = pd.to_datetime(df["noticeSdt"], format="%Y%m%d")
        print("data 변환 성공")

    else:
        print("변환할 데이터 없음")

    return df


def load_to_bigquery(**context):
    bigquery_schema = [
        bigquery.SchemaField("desertionNo", "INTEGER"),
        bigquery.SchemaField("filename", "STRING"),
        bigquery.SchemaField("happenDt", "DATETIME"),
        bigquery.SchemaField("happenPlace", "STRING"),
        bigquery.SchemaField("kindCd", "STRING"),
        bigquery.SchemaField("colorCd", "STRING"),
        bigquery.SchemaField("age", "STRING"),
        bigquery.SchemaField("weight", "STRING"),
        bigquery.SchemaField("noticeNo", "STRING"),
        bigquery.SchemaField("noticeSdt", "DATETIME"),
        bigquery.SchemaField("noticeEdt", "DATETIME"),
        bigquery.SchemaField("popfile", "STRING"),
        bigquery.SchemaField("processState", "STRING"),
        bigquery.SchemaField("sexCd", "STRING"),
        bigquery.SchemaField("neuterYn", "STRING"),
        bigquery.SchemaField("specialMark", "STRING"),
        bigquery.SchemaField("careNm", "STRING"),
        bigquery.SchemaField("careTel", "STRING"),
        bigquery.SchemaField("careAddr", "STRING"),
        bigquery.SchemaField("orgNm", "STRING"),
        bigquery.SchemaField("chargeNm", "STRING"),
        bigquery.SchemaField("officetel", "STRING"),
        bigquery.SchemaField("noticeComment", "STRING"),
    ]

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.environ["AIRFLOW_HOME"], "keys", "load_to_bigquery_raw_data.json"
    )
    project_id = context["params"]["project_id"]
    dataset_id = context["params"]["dataset_id"]
    table_id = context["params"]["table_id"]
    df = context["ti"].xcom_pull(task_ids="transform_data")

    # BigQuery 클라이언트 인스턴스 생성
    bigquery_client = bigquery.Client()

    # 데이터프레임을 로드할 테이블 경로 설정
    table_path = f"{project_id}.{dataset_id}.{table_id}"

    # 테이블이 이미 존재하는지 확인
    try:
        bigquery_client.get_table(table_path)
        table_exists = True
    except Exception as e:
        print(f"{e}")
        table_exists = False

    # 테이블이 존재하는 경우 테이블 삭제
    if table_exists:
        bigquery_client.delete_table(table_path)
        table_exists = False

    try:
        # 새로운 테이블 생성
        schema = bigquery_schema
        table_ref = bigquery_client.create_table(
            bigquery.Table(table_path, schema=schema)
        )

        # 데이터프레임을 대상 테이블로 적재
        job_config = bigquery.LoadJobConfig(schema=bigquery_schema)
        job = bigquery_client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()  # Job 실행 완료 대기
    except Exception as e:
        print("load_to_bigquery - 오류 발생 : ", e)
        raise AirflowException(f"오류 발생. {e}")


extract = PythonOperator(
    dag=dag,
    task_id="extract_data_OpenAPI",
    python_callable=extract_data_OpenAPI,
    params={
        "OpenAPI_URL": Variable.get("OpenAPI_URL"),
        "OpenAPI_KEY": Variable.get("OpenAPI_KEY"),
    },
)

upload_file = PythonOperator(
    dag=dag,
    task_id="upload_data_GCS",
    python_callable=upload_data_GCS,
)

read = PythonOperator(
    dag=dag,
    task_id="read_data_from_storage",
    python_callable=read_data_from_storage,
    params={
        "bucket_name": "strayanimal-bucket",
    },
)


transform = PythonOperator(
    dag=dag,
    task_id="transform_data",
    python_callable=transform_data,
)
load = PythonOperator(
    dag=dag,
    task_id="load_to_bigquery",
    python_callable=load_to_bigquery,
    params={
        "dataset_id": "raw_data",
        "table_id": "animal_daily",
        "project_id": "strayanimal",
    },
)

extract >> upload_file >> read >> transform >> load
