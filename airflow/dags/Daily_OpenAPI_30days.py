import asyncio
import json
import os
from datetime import datetime, timedelta

import aiohttp
import pandas as pd
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from dateutil.relativedelta import relativedelta
from google.cloud import bigquery, storage
from pytz import timezone

from plugins import slack

OPENAPI_URL = Variable.get("OpenAPI_URL")
OPENAPI_KEY = Variable.get("OpenAPI_KEY")
DAG_ID = "Daily_OpenAPI_30days"
dag = DAG(
    DAG_ID,
    schedule_interval="5 15 * * *",
    start_date=datetime(2023, 6, 25),
    catchup=False,
    default_args={
        "on_failure_callback": slack.on_failure_callback,
    },
)


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [
        (start + timedelta(days=i)).strftime("%Y%m%d")
        for i in range((end - start).days)
    ]
    return dates


async def fetch(client, params):
    async with client.get(OPENAPI_URL, params=params, timeout=3) as resp:
        assert resp.status == 200
        return await resp.text()


async def request_OpenAPI(date, params, MAX_RETRIES=10):
    for _ in range(MAX_RETRIES):
        params["bgnde"] = date
        params["endde"] = date
        try:
            async with aiohttp.ClientSession() as client:
                res = await fetch(client, params)

            if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in res:
                raise Exception(
                    "공공데이터 OpenAPI Server error: SERVICE_KEY_IS_NOT_REGISTERED_ERROR -> 등록되지 않은 서비스키"
                )
            else:
                df_dailydata = pd.DataFrame(
                    json.loads(res)["response"]["body"]["items"]["item"]
                )  # daily data json -> df
                print(date, "성공 데이터 :", df_dailydata.shape[0])
                break
            
        except TypeError:
            print(date, "| 등록된 유기동물 데이터가 없습니다.")
            return None
        except Exception as e:
            if e.__class__ is asyncio.exceptions.TimeoutError:
                print(date, '|', res.status_code, "ReadTimeout Error : " + str(e))
            elif e.__class__ is asyncio.exceptions.CancelledError:
                print(date, '|', res.status_code, "CancelledError Error : " + str(e))
            else:
                print(date, '|', res.status_code, str(e), '| error type :', type(e))
    else:
        print(date, "10회 이상 추출 실패, OpenAPI 서버 문제로 추출 중단")
        return None

    return df_dailydata


def extract_data_OpenAPI():
    params = {
        "serviceKey": OPENAPI_KEY,
        "bgnde": "yyyymmdd",
        "endde": "yyyymmdd",
        "numOfRows": "1000",
        "_type": "json",
    }

    today = datetime.now(timezone("Asia/Seoul")).strftime("%Y-%m-%d")
    before_one_month = (
        datetime.now(timezone("Asia/Seoul")) - relativedelta(months=1)
    ).strftime("%Y-%m-%d")
    dates = date_range(before_one_month, today)

    # 현재 실행 중인 스레드의 이벤트 루프를 가져옵니다. 만약 이벤트 루프가 없다면 새로운 이벤트 루프를 생성
    loop = asyncio.get_event_loop()

    # 각각의 request_OpenAPI() 호출을 리스트 컴프리헨션을 사용하여 생성
    futures = [request_OpenAPI(date, params) for date in dates]

    # asyncio.gather()를 사용하여 모든 Future 객체를 묶은 후, 현재 이벤트 루프를 사용하여 병렬로 실행
    # loop.run_until_complete()를 사용하여 병렬 실행이 완료될 때까지 기다립니다.
    results = loop.run_until_complete(asyncio.gather(*futures))

    # 이벤트 루프를 종료
    loop.close()

    SAVE_NAME = "strayanimal_data_" + dates[-1] + ".csv"
    LOCAL_PATH_NAME = os.path.join(
        os.environ["AIRFLOW_HOME"], "data", "strayanimal_30days_data", SAVE_NAME
    )

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

    for df_dailydata in results:
        if df_dailydata is None:
            raise AirflowException("10회 이상 추출 실패 데이터 존재 | OpenAPI 서버 문제로 추출 중단")
        else:
            result_df = pd.concat([result_df, df_dailydata], ignore_index=True)
    else:
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


def transform_data(**context):
    try:
        SAVE_NAME, LOCAL_PATH_NAME = context["ti"].xcom_pull(
            task_ids="extract_data_OpenAPI"
        )
        df = pd.read_csv(LOCAL_PATH_NAME, encoding="utf-8-sig", index_col=0)
        today = datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d")

        df["desertionNo"] = df["desertionNo"].astype(int)

        df["created_date"] = pd.to_datetime(today, format="%Y%m%d")
        df["happenDt"] = pd.to_datetime(df["happenDt"], format="%Y%m%d")
        df["noticeEdt"] = pd.to_datetime(df["noticeEdt"], format="%Y%m%d")
        df["noticeSdt"] = pd.to_datetime(df["noticeSdt"], format="%Y%m%d")
        # print(df.info())

        TRANSFORM_SAVE_NAME = "transform" + SAVE_NAME
        TRANSFORM_LOCAL_PATH_NAME = os.path.join(
            os.environ["AIRFLOW_HOME"],
            "data",
            "strayanimal_30days_data",
            TRANSFORM_SAVE_NAME,
        )
        df.to_csv(TRANSFORM_LOCAL_PATH_NAME, encoding="utf-8-sig")
        return TRANSFORM_SAVE_NAME, TRANSFORM_LOCAL_PATH_NAME
    except Exception as e:
        print("transform_data - 오류 발생 : ", e)
        raise AirflowException(f"오류 발생. {e}")


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

    TRANSFORM_SAVE_NAME, TRANSFORM_LOCAL_PATH_NAME = context["ti"].xcom_pull(
        task_ids="transform_data"
    )
    df = pd.read_csv(TRANSFORM_LOCAL_PATH_NAME, encoding="utf-8-sig", index_col=0)

    # 데이터프레임을 로드할 테이블 경로 설정
    table_path = f"{project_id}.{dataset_id}.{table_id}"
    temp_table_path = f"{project_id}.{dataset_id}.{temp_table_id}"

    # BigQuery 클라이언트 인스턴스 생성
    bigquery_client = bigquery.Client()

    try:
        # 테이블 존재 여부 확인
        bigquery_client.get_table(table_path)
        print(f"{table_path} 테이블 존재")
        table_exists = True
    except Exception as e:
        print(f"{e} : {table_path} 테이블 존재하지 않음")
        table_exists = False
        pass

    # 테이블가 존재하지 않는 경우에만 새로운 테이블 생성
    if not table_exists:
        schema = bigquery_schema
        bigquery_client.create_table(bigquery.Table(table_path, schema=schema))
    else:
        bigquery_client.get_table(table_path)

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

        print("load_to_bigquery success")
    except Exception as e:
        print("load_to_bigquery failed")
        raise AirflowException(f"animal_info 테이블 적재 실패! - {e}")


extract = PythonOperator(
    dag=dag,
    task_id="extract_data_OpenAPI",
    python_callable=extract_data_OpenAPI,
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
