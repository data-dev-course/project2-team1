from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
import os
import pandas as pd
import numpy as np

path = "본인의 KEY"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
before_one_day = (datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")
bucket_name = "strayanimal-bucket"
file_name = f"raw-data/strayanimal-datas/strayanimal_data_{before_one_day}.csv"
project_id = "strayanimal"
dataset_id = "raw_data"
table_id = "animal_info"


storage_client = storage.Client()
bigquery_client = bigquery.Client()
table_ref = bigquery_client.dataset(dataset_id, project=project_id).table(table_id)


def read_data_from_storage(bucket_name, file_name):
    blob = storage_client.get_bucket(bucket_name).get_blob(file_name)
    csv_data = blob.download_as_text().splitlines()
    df = pd.read_csv(io.StringIO("\n".join(csv_data)))
    return df


def get_existing_data(project_id, dataset_id, table_id):
    # table = bigquery_client.get_table(table_ref)
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.{table_id}`
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()
    existing_data = {row.desertionNo: row.processState for row in results}
    return existing_data


def update_data(project_id, dataset_id, table_id, update_df):
    if len(update_df) > 0:
        # Convert the 'desertionNo' column values to a list
        desertion_nos = update_df["desertionNo"].tolist()

        # Filter the existing data based on 'desertionNo'
        filter_condition = (
            f"desertionNo IN UNNEST([{','.join(str(n) for n in desertion_nos)}])"
        )
        query = f"SELECT desertionNo, processState FROM `{project_id}.{dataset_id}.{table_id}` WHERE {filter_condition}"
        existing_data = bigquery_client.query(query).to_dataframe()

        # Update the 'processState' values in the existing data based on 'desertionNo' matching
        for _, row in existing_data.iterrows():
            desertion_no = row["desertionNo"]
            process_state = update_df.loc[
                update_df["desertionNo"] == desertion_no, "processState"
            ].values[0]

            update_query = f"UPDATE `{project_id}.{dataset_id}.{table_id}` SET processState = '{process_state}' WHERE desertionNo = {desertion_no}"
            bigquery_client.query(update_query)

        print("데이터 업데이트 완료.")
    else:
        print("데이터가 없습니다.")


def insert_data(project_id, dataset_id, table_id, insert_data):
    """
    새로운 데이터를 Batch Insert로 BigQuery에 삽입합니다.

    Args:
        project_id (str): 프로젝트 ID
        dataset_id (str): 데이터셋 ID
        table_id (str): 테이블 ID
        insert_data (pd.DataFrame): 삽입할 데이터가 담긴 데이터프레임
    """
    if len(insert_data) > 0:
        # Convert DataFrame to list of dictionaries
        insert_rows = insert_data.replace({np.nan: None}).to_dict(orient="records")

        # Perform the batch insert using BigQuery client library
        errors = bigquery_client.insert_rows_json(table_ref, insert_rows)

        if errors:
            print("데이터 삽입 중 오류가 발생했습니다:")
            for error in errors:
                print(error)
        else:
            print(f"삽입된 레코드 수: {len(insert_data)}")

        print("데이터 삽입 완료.")
    else:
        print("추가할 데이터가 없습니다.")


def process_data(bucket_name, file_name, project_id, dataset_id, table_id):
    # def process_data(bucket_name, file_name, project_id, dataset_id, table_id):
    df = read_data_from_storage(bucket_name, file_name)
    existing_data = get_existing_data(project_id, dataset_id, table_id)

    # 새로 추가해야 할 데이터 필터링
    new_df = df[~df["desertionNo"].isin(existing_data.keys())].copy()
    new_df = new_df.rename(columns={"Unnamed: 0": "int64_field_0"})

    # 업데이트해야 할 데이터 필터링
    update_df = df[
        df["desertionNo"].isin(existing_data.keys())
        & (df["processState"] != df["desertionNo"].map(existing_data))
    ].copy()
    update_df = update_df.rename(columns={"Unnamed: 0": "int64_field_0"})

    ## 기존 빅쿼리에 들어있는 데이터 업데이트
    update_data(
        project_id, dataset_id, table_id, update_df[["desertionNo", "processState"]]
    )

    # # 새롭게 추가해야 할 데이터 합치고 삽입하기
    # result_data = pd.concat([new_df, update_df], ignore_index=True)
    insert_data(project_id, dataset_id, table_id, new_df)

    # 모든 작업 후 테이블 데이터 개수 확인
    print(f"update_df  : {len(update_df)}, new_df : {len(new_df)}")
    print(f"Number of rows in the {file_name} file: {len(df)}")
    new_df.to_csv(
        f'/home/ubuntu/openAPI/data/new_data_{(datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")}.csv'
    )
    update_df.to_csv(
        f'/home/ubuntu/openAPI/data/changed_data_{(datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")}.csv'
    )
    print(
        f'save the new_df file {(datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")}.csv '
    )
    print(
        f'save the update_df file {(datetime.now() - relativedelta(days=1)).strftime("%Y%m%d")}.csv '
    )


def main():
    print("ㅡ" * 20)
    print("Start animal_info_bugquery_update")
    process_data(bucket_name, file_name, project_id, dataset_id, table_id)
    print("End animal_info_bugquery_update", datetime.now())
    print("ㅡ" * 20)


if __name__ == "__main__":
    main()
