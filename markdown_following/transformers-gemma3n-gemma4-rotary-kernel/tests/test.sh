#!/usr/bin/env bash
# Standardized test runner: executes pytest and writes a binary reward.
# Reward goes to /logs/verifier/reward.txt as the literal "0" or "1".

set -u

mkdir -p /logs/verifier

cd /workspace/transformers || exit 1

cd /tests || cd /workspace/task/tests || true

python -m pytest /tests/test_outputs.py -v --tb=short \
    -o cache_dir=/tmp/.pytest_cache \
    --json-report --json-report-file=/logs/verifier/ctrf.json 2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
