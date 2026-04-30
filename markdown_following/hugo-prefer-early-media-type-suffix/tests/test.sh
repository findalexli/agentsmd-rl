#!/bin/bash
# Standardized test runner. Writes binary reward to /logs/verifier/reward.txt
# directly from pytest's exit code. Do not add task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v \
    --tb=short \
    --json-report --json-report-file=/logs/verifier/report.json \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (no rubric judge wired in here; eval_manifest's rubric is consumed offline)
