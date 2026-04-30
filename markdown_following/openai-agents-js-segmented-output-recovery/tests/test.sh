#!/bin/bash
# Standardized test harness — DO NOT add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

# Pytest is preinstalled in the image (see Dockerfile). Run the test suite.
cd /tests
pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No subjective rubric judge step in this task; rewards come from pytest only.)

exit 0
