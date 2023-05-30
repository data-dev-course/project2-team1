from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
import os
import pandas as pd

path = "./strayanimal-61531c578dbe.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=path

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
    df = pd.read_csv(io.StringIO('\n'.join(csv_data)))[['desertionNo','processState','happenDt']]
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
    table_ref = bigquery_client.dataset(dataset_id, project=project_id).table(table_id)
    table = bigquery_client.get_table(table_ref)
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

def insert_changed_data(project_id, dataset_id, table_id, changed_data):
    """
    변경된 데이터를 BigQuery에 삽입합니다.
    
    Args:
        project_id (str): 프로젝트 ID
        dataset_id (str): 데이터셋 ID
        table_id (str): 테이블 ID
        changed_data (pd.DataFrame): 변경된 데이터가 담긴 데이터프레임
    """
    bigquery_client = bigquery.Client()
    if len(changed_data) > 0:
        values = []
        for _, row in changed_data.iterrows():
            values.append("({}, '{}', DATE '{}')".format(row.desertionNo, row.processState, datetime.strptime(str(row.happenDt), '%Y%m%d').strftime('%Y-%m-%d')))
        insert_query = """
        INSERT INTO {}.{} ({}, {}, {})
        VALUES {}
        """.format(dataset_id, table_id, 'desertionNo', 'processState', 'stateUpdateDt', ','.join(values))
        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = False
        query_job = bigquery_client.query(insert_query, job_config=job_config)
        query_job.result()
        print(f"변경된 레코드 수: {len(changed_data)}")
        print(changed_data)
        
        print("데이터 삽입 완료.")
    else:
        print("변경된 데이터 없음.")
        
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
    changed_data = df[df['desertionNo'].map(existing_data) != df['processState']]
    insert_changed_data(project_id, dataset_id, table_id, changed_data)


def main():
    before_one_day = (datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")
    bucket_name = 'strayanimal-bucket'
    file_name = f"raw-data/strayanimal_data_{before_one_day}.csv"
    project_id = 'strayanimal'
    dataset_id = 'raw_data'
    table_id = 'animal_status'

    process_data(bucket_name, file_name, project_id, dataset_id, table_id)

if __name__ == '__main__':
    main()
    
    
