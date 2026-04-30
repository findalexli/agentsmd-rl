#!/bin/bash
# Standardized test harness — DO NOT MODIFY task-specific logic here.
set -u

mkdir -p /logs/verifier

# Run pytest. Reward is the literal "0"/"1" written from pytest's exit code.
cd /workspace/airflow

python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
