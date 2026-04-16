#!/bin/bash
set -e

apt-get install -y python3-pytest 2>/dev/null || true

cd /workspace/router

python3 -m pytest /tests/test_outputs.py -v --tb=short --cache-clear 2>&1
PYTEST_EXIT=$?

# Write reward based on pytest exit code
# 0 = all passed (reward=1), non-zero = some failed (reward=0)
if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "Reward written: 1 (all tests passed)"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Reward written: 0 (some tests failed)"
fi

cat /logs/verifier/reward.txt