#!/usr/bin/env bash
# Standardized test runner. Runs pytest on test_outputs.py and writes the
# binary reward ("0" or "1") to /logs/verifier/reward.txt based purely on the
# pytest exit code. CTRF JSON is also emitted for downstream auditing.

set -u
mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit: $status"
echo "reward: $(cat /logs/verifier/reward.txt)"
