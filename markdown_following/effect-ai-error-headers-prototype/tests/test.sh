#!/usr/bin/env bash
# Standardized test runner — DO NOT add task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /tests
python3 -m pytest \
    test_outputs.py \
    -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved for harness-side rubric evaluation. Do not exit before this point.

exit $status
