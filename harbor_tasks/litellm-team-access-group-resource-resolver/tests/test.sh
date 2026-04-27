#!/usr/bin/env bash
# Standardized test runner — DO NOT add task-specific logic here.

set -uo pipefail

mkdir -p /logs/verifier

# Run the task's tests.
python -m pytest /tests/test_outputs.py \
    -v \
    --tb=short \
    -p no:cacheprovider \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- Reward ---"
cat /logs/verifier/reward.txt
echo

echo "--- LLM Judge ---"
if [ -f /tests/standalone_judge.py ]; then
    python /tests/standalone_judge.py || true
fi

exit 0
