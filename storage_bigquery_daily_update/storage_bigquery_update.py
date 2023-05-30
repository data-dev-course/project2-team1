# pip install google-cloud-storage
# pip install google-cloud-bigquery

from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os




# Google Cloud Storage와 BigQuery 인증 정보 설정
# path에는 GCP 에서 할당받은 Serice Key가 필요 
path = "{INPUT YOUR SERVICE KEY}"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=path

before_one_day = (datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")
storage_client = storage.Client()
bigquery_client = bigquery.Client()






# 업데이트 감지 및 BigQuery 업데이트 함수 정의
def update_bigquery(bucket_name, file_name):
    # 이벤트 정보에서 업데이트된 파일의 경로 추출
    file_path = f"gs://{bucket_name}/{file_name}"

    # BigQuery 테이블 정보
    dataset_id = 'raw_data'
    table_id = 'animal_info'

    # BigQuery 테이블에 업데이트 수행
    table_ref = bigquery_client.dataset(dataset_id).table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.autodetect = True

    load_job = bigquery_client.load_table_from_uri(
        file_path, table_ref, job_config=job_config
    )
    load_job.result()  # 업로드 작업 완료 대기

    
    
    
    if load_job.state == 'DONE':
        print(f"Updated BigQuery table {table_id} with data from {file_path}")
    else:
        print(f"Failed to update BigQuery table {table_id} with data from {file_path}")





def check_update():
    # Google Cloud Storage 에 적재되어있는 데이터를 읽어오기위해 
    # 버킷 이름과 파일 이름 지정 ( 매일 전 날짜의 csv를 읽어와 업데이트 )
    bucket_name = 'strayanimal-bucket'
    file_name = f"raw-data/strayanimal_data_{before_one_day}.csv"
    
    
    
    update_bigquery(bucket_name, file_name)



def main() :
    check_update()

if __name__ == "__main__":
    main()
