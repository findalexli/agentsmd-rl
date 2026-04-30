#!/bin/bash
# Standardized test harness — DO NOT add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier
cd /workspace/litellm

# Run the test suite. Reward is the literal pytest exit code.
python -m pytest /tests/test_outputs.py -v --tb=short --color=no \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] pytest exit=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"
