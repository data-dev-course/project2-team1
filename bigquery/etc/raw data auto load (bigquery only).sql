/*
Upload CSV
- 스키마 자동으로 감지해서 데이터 로드
- 데이터 소스에서 무작위로 최대 500행의 데이터를 스캔해 대표 샘플로 사용
- 가장 많은 필드를 포함하는 행을 기반으로 샘플링해 스키마 추론을 진행
- Parquet, Avro, Orc파일의 경우 추론된 스키마를 재정의할 수 있음
 */
LOAD DATA OVERWRITE raw_data.animal_register
FROM FILES (
  format = 'CSV',
  uris = ['gs://strayanimal-bucket/raw-data/animal_register.csv']);

LOAD DATA OVERWRITE raw_data.animal_shelter
FROM FILES (
  format = 'CSV',
  uris = ['gs://strayanimal-bucket/raw-data/animal_shelter.csv']);

LOAD DATA OVERWRITE raw_data.family_income_info
FROM FILES (
  format = 'CSV',
  uris = ['gs://strayanimal-bucket/raw-data/family_income_info_20211203.csv']);

LOAD DATA OVERWRITE raw_data.monthly_population
FROM FILES (
  format = 'CSV',
  uris = ['gs://strayanimal-bucket/raw-data/monthly_population.csv']);
/*
Upload Json
- 스키마 자동으로 감지하는 방법은 CSV와 동일
- Json파일 형식을 맞춰줘야 정상적으로 로드됨
- Json list 형식이 아닌 줄바꿈 형식으로 해야함
- ex)
1. 리스트 형식 Json
[
  {'name':'tj', 'age': '1'},
  {'name':'dh', 'age' : '3'}
]

2. 줄바꿈 형식 Json
{'name':'tj', 'age': '1'}
{'name':'dh', 'age' : '3'}
 */
LOAD DATA OVERWRITE raw_data.test_json
FROM FILES (
  format = 'JSON',
  uris = ['gs://strayanimal-bucket/raw-data/animal_shelter_test.json']);

