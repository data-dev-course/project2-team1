from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
import os
import pandas as pd

path = "본인의 KEY"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path


def read_data_from_storage(bucket_name, file_name):
    """
    Google Cloud Storage에서 데이터를 읽어옵니다.

    Args:
        bucket_name (str): 버킷 이름
        file_name (str): 파일 이름

    Returns:
        pd.DataFrame: 읽어온 데이터를 담은 데이터프레임
    """
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).get_blob(file_name)
    csv_data = blob.download_as_text().splitlines()
    df = pd.read_csv(io.StringIO("\n".join(csv_data)))[
        ["desertionNo", "processState", "happenDt"]
    ]
    return df


def get_existing_data(project_id, dataset_id, table_id):
    """
    BigQuery에서 기존 데이터를 가져옵니다.

    Args:
        project_id (str): 프로젝트 ID
        dataset_id (str): 데이터셋 ID
        table_id (str): 테이블 ID

    Returns:
        dict: desertionNo를 키로, processState를 값으로 하는 기존 데이터의 딕셔너리
    """
    bigquery_client = bigquery.Client()

    query = f"""
    SELECT *
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY desertionNo ORDER BY stateUpdateDt DESC) AS rn
        FROM `{project_id}.{dataset_id}.{table_id}`
    ) t
    WHERE rn = 1
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()
    existing_data = {row.desertionNo: row.processState for row in results}
    return existing_data


def insert_changed_data(project_id, dataset_id, table_id, data):
    """
    변경된 데이터를 BigQuery에 삽입합니다.

    Args:
        project_id (str): 프로젝트 ID
        dataset_id (str): 데이터셋 ID
        table_id (str): 테이블 ID
        data (pd.DataFrame): 변경된 데이터가 담긴 데이터프레임
    """
    bigquery_client = bigquery.Client()
    if len(data) > 0:
        values = []
        for _, row in data.iterrows():
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
            dataset_id,
            table_id,
            "desertionNo",
            "processState",
            "stateUpdateDt",
            ",".join(values),
        )
        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = False
        query_job = bigquery_client.query(insert_query, job_config=job_config)
        query_job.result()
        print(f"Number of modified records: {len(data)}")
        print("Data insertion complete.")
    else:
        print("There is no data to update.")


def process_data(bucket_name, file_name, project_id, dataset_id, table_id):
    """
    데이터 처리를 수행합니다.

    Args:
        bucket_name (str): 버킷 이름
        file_name (str): 파일 이름
        project_id (str): 프로젝트 ID
        dataset_id (str): 데이터셋 ID
        table_id (str): 테이블 ID
    """
    df = read_data_from_storage(bucket_name, file_name)

    existing_data = get_existing_data(project_id, dataset_id, table_id)
    # changed_data = df[df['desertionNo'].map(existing_data) != df['processState']]
    # new_data = df[~df['desertionNo'].isin(existing_data.keys())]
    new_data = df[~df["desertionNo"].isin(existing_data.keys())].copy()
    changed_data = df[
        df["desertionNo"].isin(existing_data.keys())
        & (df["processState"] != df["desertionNo"].map(existing_data))
    ].copy()

    print(f"changed_data  : {len(changed_data)}, new_data : {len(new_data)}")
    result_data = pd.concat([changed_data, new_data], ignore_index=True)
    result_data["happenDt"] = int(datetime.today().strftime("%Y%m%d"))

    insert_changed_data(project_id, dataset_id, table_id, result_data)

    print(f"Number of rows in the {file_name} file: {len(df)}")


def main():
    before_one_day = (datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")
    bucket_name = "strayanimal-bucket"
    file_name = f"raw-data/strayanimal-datas/strayanimal_data_{before_one_day}.csv"
    project_id = "strayanimal"
    dataset_id = "raw_data"
    table_id = "animal_status"
    print("ㅡ" * 20)
    print("Start animal_status_bugquery_update")
    process_data(bucket_name, file_name, project_id, dataset_id, table_id)
    print("End animal_status_bugquery_update", datetime.now())

    print("ㅡ" * 20)


if __name__ == "__main__":
    main()
