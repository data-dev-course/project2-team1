from airflow import DAG
from airflow.macros import *
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from airflow.models import Variable

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from google.cloud import storage
from google.cloud import bigquery


DAG_ID = "Daily_OpenAPI_30days"
dag = DAG(
    DAG_ID,
    schedule_interval="5 15 * * *",
    start_date=datetime(2023, 6, 25),
    catchup=False,
)


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [
        (start + timedelta(days=i)).strftime("%Y%m%d")
        for i in range((end - start).days)
    ]
    return dates


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
        ]
    )

    daily_data_cnt = 0
    MAX_RETRIES = 10
    today = datetime.now(timezone("Asia/Seoul")).strftime("%Y-%m-%d")
    before_one_month = (
        datetime.now(timezone("Asia/Seoul")) - relativedelta(months=1)
    ).strftime("%Y-%m-%d")

    dates = date_range(before_one_month, today)
    params = {
        "serviceKey": OpenAPI_KEY,
        "bgnde": "yyyymmdd",
        "endde": "yyyymmdd",
        "numOfRows": "1000",
        "_type": "json",
    }

    for date in dates:
        params["bgnde"] = date
        params["endde"] = date
        for _ in range(MAX_RETRIES):
            try:
                my_response = requests.get(OpenAPI_URL, params=params, timeout=5)

                if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in my_response.text:
                    raise Exception(
                        "공공데이터 OpenAPI Server error: SERVICE_KEY_IS_NOT_REGISTERED_ERROR"
                    )
                else:
                    df_dailydata = pd.DataFrame(
                        json.loads(my_response.text)["response"]["body"]["items"][
                            "item"
                        ]
                    )  # daily data json -> df
                    result_df = pd.concat([result_df, df_dailydata], ignore_index=True)
                    daily_data_cnt += df_dailydata.shape[0]
                    print(
                        date,
                        "성공 데이터 :",
                        df_dailydata.shape[0],
                        "/",
                        "총 데이터 :",
                        daily_data_cnt,
                    )
                    break

            except Exception as e:
                print(date, "error :", e)
        else:
            raise AirflowException("10회 이상 추출 실패, OpenAPI 서버 문제로 추출 중단")

    SAVE_NAME = "strayanimal_data_" + dates[-1] + ".csv"

    LOCAL_PATH_NAME = os.path.join(
        os.environ["AIRFLOW_HOME"], "data", "strayanimal_30days_data", SAVE_NAME
    )
    result_df.to_csv(LOCAL_PATH_NAME, encoding="utf-8-sig")

    return SAVE_NAME, LOCAL_PATH_NAME, result_df


def upload_data_GCS(**context):
    SAVE_NAME, LOCAL_PATH_NAME = context["ti"].xcom_pull(
        task_ids="extract_data_OpenAPI"
    )[:2]
    # print(SAVE_NAME, LOCAL_PATH_NAME)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.environ["AIRFLOW_HOME"], "keys", "strayanimal-bucket.json"
    )

    bucket_name = "strayanimal-bucket"  # bucket 이름
    BUCKET_PATH = "raw-data/strayanimal-datas/"  # bucket 내부 위치
    destination_blob_name = BUCKET_PATH + SAVE_NAME  # 업로드 위치 + 업로드 파일 이름

    # GCP Storage에 client 연결
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 파일 업로드
    blob.upload_from_filename(LOCAL_PATH_NAME, content_type="text/csv")
    print("Cloud Storage 적재 성공", datetime.now())


def transform_data(**context):
    df = context["ti"].xcom_pull(task_ids="extract_data_OpenAPI")[2]
    today = datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d")

    df["desertionNo"] = df["desertionNo"].astype(int)

    df["created_date"] = pd.to_datetime(today, format="%Y%m%d")
    df["happenDt"] = pd.to_datetime(df["happenDt"], format="%Y%m%d")
    df["noticeEdt"] = pd.to_datetime(df["noticeEdt"], format="%Y%m%d")
    df["noticeSdt"] = pd.to_datetime(df["noticeSdt"], format="%Y%m%d")
    # print(df.info())

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
        bigquery.SchemaField("created_date", "DATETIME"),
    ]
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.environ["AIRFLOW_HOME"], "keys", "load_to_bigquery_raw_data.json"
    )
    project_id = context["params"]["project_id"]
    dataset_id = context["params"]["dataset_id"]
    table_id = context["params"]["table_id"]
    temp_table_id = "daily_temp"
    df = context["ti"].xcom_pull(task_ids="transform_data")

    # 데이터프레임을 로드할 테이블 경로 설정
    table_path = f"{project_id}.{dataset_id}.{table_id}"
    temp_table_path = f"{project_id}.{dataset_id}.{temp_table_id}"

    # 이전 작업을 위한 백업 테이블명
    backup_table_id = "backup_table"

    # BigQuery 클라이언트 인스턴스 생성
    bigquery_client = bigquery.Client()

    try:
        # 이전 작업을 위해 원본 테이블을 백업
        backup_table_ref = bigquery_client.copy_table(table_path, backup_table_id)
    except:
        # 백업 실패 시 처리할 예외 처리 로직 작성
        pass

    try:
        # 테이블 존재 여부 확인
        bigquery_client.get_table(table_path)
        table_exists = True
    except:
        table_exists = False
        pass

    # 테이블가 존재하지 않는 경우에만 새로운 테이블 생성
    if not table_exists:
        schema = bigquery_schema
        table_ref = bigquery_client.create_table(
            bigquery.Table(table_path, schema=schema)
        )
    else:
        table_ref = bigquery_client.get_table(table_path)

    try:
        # 데이터프레임을 임시 테이블로 저장
        job_config = bigquery.LoadJobConfig(schema=bigquery_schema)
        job = bigquery_client.load_table_from_dataframe(
            df, temp_table_path, job_config=job_config
        )
        job.result()  # Job 실행 완료 대기

        # 임시 테이블의 데이터를 대상 테이블로 삽입 (중복 제거됨)
        query = f"""
            INSERT INTO {table_path}
            SELECT t.*
            FROM {temp_table_path} AS t
            EXCEPT DISTINCT
            SELECT *
            FROM {table_path}
        """
        job = bigquery_client.query(query)
        job.result()  # Job 실행 완료 대기

        # 임시 테이블 삭제
        bigquery_client.delete_table(temp_table_path)

        print("success")
    except:
        # 작업 실패 시 이전 상태로 복구
        bigquery_client.copy_table(backup_table_ref, table_path)

        # 실패한 작업으로 인해 생성된 임시 테이블을 삭제
        bigquery_client.delete_table(temp_table_path)

        print("failed")


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
        "table_id": "animal_info",
        "project_id": "strayanimal",
    },
)


extract >> [upload_file, transform] >> load