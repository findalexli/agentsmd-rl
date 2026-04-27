#!/usr/bin/env bash
# Standardized test runner. Reward is the literal "0" or "1" derived from
# pytest's exit code. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    -v \
    --tb=short \
    --json-report \
    --json-report-file=/logs/verifier/pytest_report.json \
    test_outputs.py \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Surface the log to stdout so harness operators can debug.
cat /logs/verifier/pytest.log
echo "--- reward: $(cat /logs/verifier/reward.txt) ---"
exit $PYTEST_RC
