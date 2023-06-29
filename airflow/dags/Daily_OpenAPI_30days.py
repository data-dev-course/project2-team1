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

    return SAVE_NAME, LOCAL_PATH_NAME


def upload_data_GCS(**context):
    SAVE_NAME, LOCAL_PATH_NAME = context["ti"].xcom_pull(
        task_ids="extract_data_OpenAPI"
    )
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
