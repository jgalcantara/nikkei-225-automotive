import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator

from download_data import scrape_components
from download_data import download_historical_data
from download_data import download_info_data
from upload_to_gcs import upload_to_gcs

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'nikkei_225_auto')

industry = "Automobiles & Auto parts"
code_file = "n225_code.parquet"
parquet_file = "n225_comp_hist.parquet"
info_file = "n225_info.parquet"
url = "https://indexes.nikkei.co.jp/en/nkave/index/component?idx=nk225"

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    download_components_task = PythonOperator(
        task_id="download_components_task",
        python_callable=scrape_components,
        op_kwargs={"url": url,
                   "industry": industry},
    )

    download_dataset_task = PythonOperator(
        task_id="download_dataset_task",
        python_callable=download_historical_data,
        op_kwargs={"ticker_file": f"{path_to_local_home}/{code_file}"},
    )

    download_info_task = PythonOperator(
        task_id="download_info_task",
        python_callable=download_info_data,
        op_kwargs={"ticker_file": f"{path_to_local_home}/{code_file}"},
    )    

    for file in [code_file, parquet_file, info_file]:
        local_to_gcs_task = PythonOperator(
            task_id=f"local_to_gcs_task_{file[:9]}",
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": f"raw/{file}",
                "local_file": f"{path_to_local_home}/{file}",
            },
        )

        bigquery_external_table_task = BigQueryCreateExternalTableOperator(
            task_id=f"bigquery_external_table_task_{file[:9]}",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": f"ext_{file[:9]}",
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [f"gs://{BUCKET}/raw/{file}"],
                },
            },
        )
        
        download_components_task >> download_dataset_task >> download_info_task >> local_to_gcs_task >> bigquery_external_table_task