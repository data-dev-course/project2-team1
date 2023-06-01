import os
import datetime
from google.cloud import storage
from datetime import datetime, timedelta


KEY_PATH = 'google credential json KEY의 PATH'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=KEY_PATH

# Testcode
# storage_client = storage.Client()
# buckets = list(storage_client.list_buckets())
# print(buckets)

yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")
bucket_name = 'bucket'    # 서비스 계정 생성한 bucket 이름 입력
source_file_path = ''    # GCP에 업로드할 폴더 절대경로
source_file_name = 'strayanimal_data_' + yesterday + '.csv' 

BUCKET_PATH = 'raw-data/~~/' # Cloud storage의 bucket 패치 지정
destination_blob_name = BUCKET_PATH + '원하는 이름'+ yesterday +'.csv'   # 저장 이름  # 업로드할 파일을 GCP에 저장할 때의 이름

try:    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path+source_file_name)
    print('Data Uploader Cloud Storage 적재 성공', datetime.now())
except Exception as e:
    print(e)