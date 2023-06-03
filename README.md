# Animal Stat-us Tracker
## **유기동물 조회 API를 이용한 보호소 및 계류상태 분석**
- 프로젝트 기간 : 2023.05.29 ~ 2023.06.02
- 유기된 동물의 데이터를 주기적 크롤링, ETL를 통하여 생성한 데이터를 GoogleCloudStorage, GoogleBigquery를 활용하여 적재
- Apache Superset를 활용한 대시보드 제작
- Firebase를 통한 인포그래픽 제작

## 팀 구성
|    | 강다혜 | 박태준 | 전성현 | 최민수 |
| :---: | :---: | :---: | :---: | :---: |
|GitHub| [@kangdaia](https://github.com/kangdaia) | [@ih-tjpark](https://github.com/ih-tjpark) | [@Jeon-peng](https://github.com/Jeon-peng) | [@usiohc](https://github.com/usiohc) |


## Tech
icon 전환 예정
| Field | Stack |
|:---:|:---|
| 프론트엔드 | <img src = "https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black"> <img src = "https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB">, <img src = "https://img.shields.io/badge/Express.js-000000?style=for-the-badge&logo=express&logoColor=white"> , <img src = "https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white"> |
| 백엔드 | <img src = "https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black"> |
| 데이터 관리 | Google Cloud Storage, Bigquery, FireStore |
| Dashboard | Superset |
| Scheduling | Crontab, 예약된 쿼리, Cloud Pub/Sub , Cloud Function |
| Cloud | <img src = "https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white"> |
| Design |   <img src="https://img.shields.io/badge/Adobe%20XD-470137?style=for-the-badge&logo=Adobe%20XD&logoColor=#FF61F6">  |


## 프로젝트 결과
### 1. 인포그래픽을 위한 웹 호스팅 ( link )
![image](https://github.com/data-dev-course/project2-team1/assets/70497132/9f42e86d-17f2-4875-8e23-f8fd18659f61)

### 2. 데이터 상태 분석을 위한 대시보드 구축
1. 유기동물보호소 현황 대시보드 
![유기동물보호소-분석-2023-06-02T13-14-03 747Z](https://github.com/data-dev-course/project2-team1/assets/70497132/6012efe2-6428-4108-b209-80ee4a30cc0d)
2. 유기동물 보호종료 현황 대시보드
![유기동물-보호종료-상태-2023-06-02T13-11-50 958Z](https://github.com/data-dev-course/project2-team1/assets/70497132/ea85cf23-01b6-4f09-81bc-ca21e363aa26)

## 시연
### 1.인포그래픽을 위한 웹 호스팅
https://github.com/data-dev-course/project2-team1/assets/70497132/513aaee9-5325-4d1a-9842-5529af6ca8fc

### 2. 데이터 상태 분석을 위한 대시보드 구축
https://github.com/data-dev-course/project2-team1/assets/70497132/6a756bbd-91d0-448a-b116-fdfd3722e3b4





## 데이터 흐름
![image](https://github.com/data-dev-course/project2-team1/assets/70497132/7f18790d-85db-4f48-b3dc-0b74cfdd7546)


## 전체 파이프라인
전체 파이프라인 사진





