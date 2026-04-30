#!/usr/bin/env bash
# Standardized test runner. DO NOT modify task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /workspace/superset

python3 -m pytest /tests/test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json 2>&1 \
    | tee /logs/verifier/pytest.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] pytest exit=${PYTEST_EXIT}, reward=$(cat /logs/verifier/reward.txt)"
exit 0
