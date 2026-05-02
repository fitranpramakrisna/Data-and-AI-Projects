from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="dummy_test_dag",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",   # ⬅️ GANTI DARI schedule_interval
    catchup=False,
    tags=["testing", "dummy"],
) as dag:

    print_hello = BashOperator(
        task_id="print_hello",
        bash_command="echo 'Hello Airflow! DAG is running successfully 🚀'",
    )

    print_hello
