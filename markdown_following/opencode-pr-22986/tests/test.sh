#!/bin/bash
# Standardized test runner. Runs pytest on test_outputs.py and writes
# a binary reward to /logs/verifier/reward.txt based on pytest's exit code.
set -u

mkdir -p /logs/verifier

cd /tests || exit 1

python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/test_output.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit: $PYTEST_RC"
exit 0
