from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryExecuteQueryOperator,
)

from datetime import datetime

excute_sql = """
    SELECT 
    desertionNo,
    happenDt,
    happenPlace,
    REGEXP_EXTRACT(kindCd, r'\[(.*?)\]') AS kindCd, 
    REGEXP_EXTRACT(kindCd, r'\] (.*)') AS kindSpcs,  
    colorCd,
    birth,
    CASE WHEN age LIKE '%(60일미만)%' THEN 0
        ELSE CAST(SUBSTRING(cast(noticeSdt AS STRING), 1, 4) AS INT) - CAST(SUBSTRING(birth, 1, 4) AS INT) +1
    END AS age,
    CASE WHEN REGEXP_CONTAINS(age, '(60일미만)') = TRUE THEN 1
        ELSE 0 END as lt60Day,
    weight,
    noticeNo,
    noticeSdt,
    noticeEdt,
    CASE WHEN processState = '보호중' THEN processState
        ELSE REGEXP_EXTRACT(processState, r'(.*)\(') END AS processState,
    REGEXP_EXTRACT(processState, r'\((.*?)\)') AS endState,
    sexCd,
    neuterYn,
    specialMark,
    careNm,
    careAddr,
    orgNm,
    chargeNm ,
    officeTel,
    noticeComment
    FROM 
        (
        SELECT
        *,
        SUBSTR(
        CASE WHEN LENGTH(REGEXP_EXTRACT(age, r'(.*)\(')) = 1
            THEN CONCAT("200",REGEXP_EXTRACT(age, r'(.*)\('))
        WHEN LENGTH(REGEXP_EXTRACT(age, r'(.*)\(')) = 2
            THEN CONCAT("20",REGEXP_EXTRACT(age, r'(.*)\('))
        ELSE
            REGEXP_EXTRACT(age, r'(.*)\(') END, 0,4) as birth
        FROM raw_data.animal_info
        )
    LIMIT 10;
    """

with DAG(
    dag_id="bigquery_transform",
    start_date=datetime(2023, 6, 26),
    schedule="20 15 * * *",
    max_active_runs=1,
    schedule_interval=None,
) as dag:
    bigquery_create_analytics_table = BigQueryExecuteQueryOperator(
        task_id="excute_query",
        gcp_conn_id="bigquery_connection",
        # 레거시SQL(true) 또는 표준SQL(false) 사용여부
        use_legacy_sql=False,
        # 쿼리 결과 저장 설적
        destination_dataset_table="strayanimal.analytics.analytics_test",
        # 대상 테이블이 이미 있는 경우 발생하는 작업 지정
        write_disposition="WRITE_TRUNCATE",
        sql=excute_sql,
    )
