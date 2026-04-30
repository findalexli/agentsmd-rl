#!/usr/bin/env bash
# Standardized test runner. Executes the pytest suite at /tests/test_outputs.py
# and writes a binary reward (literal "0" or "1") to /logs/verifier/reward.txt.

set -u

mkdir -p /logs/verifier
cd /tests

python3 -m pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no-op placeholder; harness can attach a judge if desired)

exit 0
