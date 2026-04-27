#!/usr/bin/env bash
# Standardized test runner. Pytest's exit code is the only signal.
set -u

mkdir -p /logs/verifier

cd /tests

# Run the behavioral / structural tests.
python3 -m pytest test_outputs.py -v --tb=short
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge (Track 2: optional semantic-diff judge runs externally) ---

exit $RC
