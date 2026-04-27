#!/bin/bash
# Standard test runner: runs pytest, writes binary reward from $?.
set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# Track 2 (config_edits) is evaluated by Gemini outside this script. No
# extra steps required here.
