#!/usr/bin/env bash
# Standardized test harness: runs pytest on test_outputs.py and writes
# binary reward (0 or 1) to /logs/verifier/reward.txt based on pytest's
# exit code only. Do NOT add task-specific logic here.

set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
EXIT_CODE=${PIPESTATUS[0]}

if [ "$EXIT_CODE" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
