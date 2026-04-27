#!/usr/bin/env bash
# Standardized test runner. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
