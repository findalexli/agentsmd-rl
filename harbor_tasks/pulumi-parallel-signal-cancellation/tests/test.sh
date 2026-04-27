#!/usr/bin/env bash
# Standardized harness test runner. Do not modify per task.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    test_outputs.py \
    -v \
    --tb=short \
    --no-header \
    -p no:cacheprovider \
    2>&1 | tee /logs/verifier/pytest.log

exit_code=${PIPESTATUS[0]}

if [ "${exit_code}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Future hook for rubric-based judging. Intentionally empty.
