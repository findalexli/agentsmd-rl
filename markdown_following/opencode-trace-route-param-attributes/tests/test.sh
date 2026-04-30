#!/usr/bin/env bash
# Standardized test runner. Reads pytest exit code → /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
