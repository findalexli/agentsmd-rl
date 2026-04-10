docker run --rm task-env bash -c "pip install pre-commit && pre-commit run --files airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py"
