#!/bin/bash
# Standardized verifier — runs pytest against /tests/test_outputs.py and
# writes a binary reward ("0" or "1") to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
RC=${PIPESTATUS[0]}

if [ "$RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# No-op placeholder. Rubric judging happens off-line via standalone_judge.py.
