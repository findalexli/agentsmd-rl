#!/usr/bin/env bash
# Standardized verifier: run pytest, write 0/1 reward from exit code.
set -u

mkdir -p /logs/verifier

cd /tests || { echo "0" > /logs/verifier/reward.txt; exit 0; }

# Run the pytest oracle. Reward derives from pytest's exit code only.
python -m pytest \
    test_outputs.py \
    -v \
    --tb=short \
    --ctrf /logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no rubric judge inline; Track 2 is run externally by harness)

exit 0
