#!/usr/bin/env bash
set -euo pipefail

# --- pytest runner ---
set +e
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tail -60
PYTEST_EXIT=${PIPESTATUS[0]}
set -e

# --- reward gate ---
if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Post-test semantic evaluation (Track 2 + Track 3).
# This block is reached regardless of pytest outcome.
echo "[]" > /logs/verifier/verdict.json
echo "0.5" > /logs/verifier/judge_score.txt
