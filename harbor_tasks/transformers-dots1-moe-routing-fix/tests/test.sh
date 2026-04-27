#!/usr/bin/env bash
# Standardized verifier runner. Do NOT modify task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /tests
python -m pytest -v --tb=short --color=no test_outputs.py
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
