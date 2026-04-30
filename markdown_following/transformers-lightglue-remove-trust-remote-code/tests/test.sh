#!/bin/bash
# Standardized test harness — runs pytest, writes binary reward to /logs/verifier/reward.txt.

set -u
mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short --ctrf /logs/verifier/ctrf.json test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge (placeholder; harness consumes only reward.txt) ---
# No early exit before this section.

exit 0
