#!/usr/bin/env bash
# Standardized test harness — runs pytest, writes binary reward to /logs/verifier/reward.txt.

set -u
mkdir -p /logs/verifier
cd /tests

pytest test_outputs.py \
    -v \
    --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    -o cache_dir=/tmp/.pytest_cache
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Optional rubric judge runs after pytest. Reward is already written; the judge
# is for downstream rubric scoring only and must not change reward.
if [ -f /tests/standalone_judge.py ]; then
    python3 /tests/standalone_judge.py >/logs/verifier/judge.log 2>&1 || true
fi
