docker run --rm task-env bash -c "python -m pytest airflow-core/tests/unit/utils/test_db.py 2>&1; echo EXIT:\$?"
