from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

Dag_id = "Clean_data_log"
dag = DAG(
    Dag_id,
    schedule_interval="0 15 * * *",
    start_date=datetime(2023, 6, 25),
    catchup=False,
)

clean_log = BashOperator(
    task_id="clean_log",
    bash_command=r'find $AIRFLOW_HOME/logs/ -maxdepth 2 -name "run_id=*" -type d -mtime +0 -exec rm -rf {} +',
    dag=dag,
)

clean_data = BashOperator(
    task_id="clean_data",
    bash_command=r"find $AIRFLOW_HOME/data/strayanimal_30days_data -type f -mtime +0 -exec rm -rf {} + && "
    + r"find $AIRFLOW_HOME/data/strayanimal_today_data -type f -mtime +0 -exec rm -rf {} +",
    dag=dag,
)

clean_log >> clean_data
