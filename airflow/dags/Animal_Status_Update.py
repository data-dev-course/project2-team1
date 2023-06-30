import io
from datetime import datetime

import pandas as pd
from airflow.decorators import task
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.common.hooks.base_google import GoogleBaseHook
from dateutil.relativedelta import relativedelta
from google.cloud import bigquery, storage
from pendulum import duration

PROJECT_ID = "strayanimal"
BEFORE_ONE_DAY = (datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")
GCP_CONN_ID = "gcp_conn_service"
DAG_ID = "animal_status_update"
BUCKET_NAME = "strayanimal-bucket"
FILE_NAME = f"raw-data/strayanimal-datas/strayanimal_data_{BEFORE_ONE_DAY}.csv"
TABLE_ID = "animal_status"
DATASET_ID = "raw_data"

default_args = {
    "owner": "kangdaia",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": duration(minutes=1),
}


@task
def read_bucket_file():
    """
    Google Cloud Storage에서 데이터를 읽어옵니다.

    Returns:
        pd.DataFrame: 읽어온 데이터를 담은 데이터프레임
    """
    cridential = GoogleBaseHook(gcp_conn_id=GCP_CONN_ID).get_credentials()
    storage_client = storage.Client(credentials=cridential)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILE_NAME)
    csv_data = blob.download_as_text().splitlines()
    df = pd.read_csv(io.StringIO("\n".join(csv_data)))[
        ["desertionNo", "processState", "happenDt"]
    ]
    return df


def get_exist_data_only_unique(client):
    """
    BigQuery내 값이 1개만 존재하는 데이터를 가져옴.

    Args:
        client: GCP bigquery API client

    Returns:
        dict: desertionNo를 키로, processState를 값으로 하는 기존 데이터의 딕셔너리
    """
    query = f"""
    SELECT *
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY desertionNo ORDER BY stateUpdateDt DESC, processState DESC) AS rn
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ) t
    WHERE rn = 1
    """
    query_job = client.query(query)
    results = query_job.result()
    existing_data = {row.desertionNo: row.processState for row in results}
    return existing_data


@task
def update_data_bigquery(file_df):
    """
    BigQuery에서 기존 데이터를 가져와 업데이트함.

    Args:
        file_df: 읽어온 데이터를 담은 데이터프레임
    """
    cridential = GoogleBaseHook(gcp_conn_id=GCP_CONN_ID).get_credentials()
    bigquery_client = bigquery.Client(credentials=cridential)

    current_unique_data = get_exist_data_only_unique(bigquery_client)
    new_data = file_df[~file_df["desertionNo"].isin(current_unique_data.keys())].copy()
    changed_data = file_df[
        file_df["desertionNo"].isin(current_unique_data.keys())
        & (file_df["processState"] != file_df["desertionNo"].map(current_unique_data))
    ].copy()

    print(f"changed_data  : {len(changed_data)}, new_data : {len(new_data)}")

    result_data = pd.concat([changed_data, new_data], ignore_index=True)
    result_data["happenDt"] = int(datetime.today().strftime("%Y%m%d"))

    if len(result_data) > 0:
        values = []
        for _, row in result_data.iterrows():
            values.append(
                "({}, '{}', DATE '{}')".format(
                    row.desertionNo,
                    row.processState,
                    datetime.strptime(str(row.happenDt), "%Y%m%d").strftime("%Y-%m-%d"),
                )
            )
        insert_query = """
        INSERT INTO {}.{} ({}, {}, {})
        VALUES {}
        """.format(
            DATASET_ID,
            TABLE_ID,
            "desertionNo",
            "processState",
            "stateUpdateDt",
            ",".join(values),
        )
        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = False
        query_job = bigquery_client.query(insert_query, job_config=job_config)
        query_job.result()
        print(f"Number of modified records: {len(result_data)}")
        print("Data insertion complete.")
    else:
        print("There is no data to update.")


with DAG(
    dag_id=DAG_ID,
    schedule="5 0 * * *",
    start_date=datetime(2023, 6, 27),
    catchup=False,
    default_args=default_args,
    tags=["ELT", "GCS"],
) as dag:
    start = DummyOperator(task_id="Start", dag=dag)

    gcs_object_exists = GCSObjectExistenceSensor(
        bucket=BUCKET_NAME,
        object=FILE_NAME,
        google_cloud_conn_id=GCP_CONN_ID,
        task_id="gcs_object_exists_task",
        deferrable=True,
    )

    file_df = read_bucket_file()
    bq_update = update_data_bigquery(file_df)

    end = DummyOperator(task_id="End", dag=dag)

    start >> gcs_object_exists >> file_df >> bq_update >> end
