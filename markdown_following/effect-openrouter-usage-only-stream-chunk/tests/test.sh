#!/bin/bash
# Standardized test harness. Reward is the literal exit code of pytest;
# do NOT add task-specific logic here.
set -u

mkdir -p /logs/verifier

# Pytest is pre-installed in the Dockerfile; no network at test time.
cd /tests
python3 -m pytest \
    -v \
    --tb=short \
    -o cache_dir=/tmp/.pytest_cache \
    test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No judge configured for this task; rubric scoring runs separately.)

exit "${PYTEST_RC}"
