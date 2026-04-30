#!/usr/bin/env bash
# Standard pytest runner — reward is the literal "0" or "1" from pytest's
# exit code, written to /logs/verifier/reward.txt. No grep/awk gates.
set -u
mkdir -p /logs/verifier

cd /tests
python -m pytest test_outputs.py \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no judge for this task; reward is purely pytest exit code)

exit 0
