#!/usr/bin/env bash
# Standardized verifier for harbor-style tasks.
# Runs pytest on /tests/test_outputs.py and writes a binary reward
# (literal "0" or "1") to /logs/verifier/reward.txt based on pytest's
# exit code.

set -u

mkdir -p /logs/verifier

cd /tests || exit 1

python3 -m pytest \
    /tests/test_outputs.py \
    -v --tb=short --no-header \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "reward=$(cat /logs/verifier/reward.txt)"
