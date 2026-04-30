#!/usr/bin/env bash
# Standardized test runner: runs pytest, writes binary reward to /logs/verifier/reward.txt
set -u

mkdir -p /logs/verifier

# Run pytest. CTRF JSON report enables per-test inspection.
pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    /tests/test_outputs.py
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
