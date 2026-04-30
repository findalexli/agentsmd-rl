#!/bin/bash
# Standard pytest-only verifier. Reward is taken directly from pytest's exit
# code. Do not add task-specific logic here.
set -u
mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
