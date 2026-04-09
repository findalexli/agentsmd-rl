#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Initialize Airflow database (required for DB tests)
cd /workspace/airflow
export AIRFLOW__CORE__UNIT_TEST_MODE=True
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:///:memory:
export PYTHONPATH="/workspace/airflow/airflow-core/src:/workspace/airflow/devel-common/src:/workspace/airflow/task-sdk/src:/workspace/airflow/shared:$PYTHONPATH"

# Run the tests from within the repo's uv environment
uv run --project airflow-core python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log || true

# Determine reward: all tests passed = 1, any failed = 0
if grep -q "passed" /logs/verifier/pytest.log && ! grep -E "FAILED|ERROR" /logs/verifier/pytest.log | grep -q "test_outputs.py"; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

cat /logs/verifier/reward.txt
