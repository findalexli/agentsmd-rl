#!/usr/bin/env bash
# Test harness: runs pytest tests in test_outputs.py and writes binary reward.
# Standardized boilerplate — do not add task-specific logic.

set +e

mkdir -p /logs/verifier

# Make sure pytest is on PATH (it is installed in the Dockerfile via /opt/venv).
export PATH="/opt/venv/bin:${PATH}"

cd /tests

pytest test_outputs.py -v --tb=short --color=no 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
