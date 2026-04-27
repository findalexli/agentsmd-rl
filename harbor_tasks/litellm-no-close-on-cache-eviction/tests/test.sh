#!/usr/bin/env bash
# Standardized test runner: runs pytest, writes binary reward to
# /logs/verifier/reward.txt from pytest's exit code.

set -u

mkdir -p /logs/verifier

cd /tests || { echo 0 > /logs/verifier/reward.txt; exit 1; }

python -m pytest test_outputs.py -v --tb=short 2>&1 \
    | tee /logs/verifier/test_output.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- pytest exit=$status reward=$(cat /logs/verifier/reward.txt) ---"
