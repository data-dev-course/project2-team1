from airflow import DAG
from airflow.macros import *
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from airflow.models import Variable

import os
import json
import requests
import pandas as pd
from datetime import datetime
from pytz import timezone
from google.cloud import storage

DAG_ID = "Quarter_OpenAPI_today"
dag = DAG(
    DAG_ID,
    schedule_interval="*/10 * * * *",
    start_date=datetime(2023, 6, 25),
    catchup=False,
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
            if e == 'item':
                print(today_HM + '기준', '등록된 유기동물 데이터가 없습니다.')
                break
            print(today_HM, "error :", e)
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
    SAVE_NAME, SAVE_VERSION_NAME = SAVE_NAME[:-9], SAVE_NAME[-8:-4]

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

extract >> upload_file
