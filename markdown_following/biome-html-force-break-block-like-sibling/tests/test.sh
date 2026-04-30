#!/usr/bin/env bash
# Standardized test runner. The harness invokes this; it executes pytest
# and writes a binary reward (0/1) to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved for the LLM-judge step in the harness; this script never exits
# before reaching here so the judge block stays reachable.
echo "test.sh complete; reward=$(cat /logs/verifier/reward.txt)"
exit 0
