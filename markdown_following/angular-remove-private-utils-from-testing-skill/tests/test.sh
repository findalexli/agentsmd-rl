#!/usr/bin/env bash
# Standardized test runner. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    > /logs/verifier/pytest.log 2>&1
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest.log
exit 0
