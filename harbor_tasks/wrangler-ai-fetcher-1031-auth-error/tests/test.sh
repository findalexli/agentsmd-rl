#!/usr/bin/env bash
# Standardized test runner: install pytest deps if missing, run tests, write
# a binary 0/1 reward to /logs/verifier/reward.txt based on pytest's exit
# code. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
