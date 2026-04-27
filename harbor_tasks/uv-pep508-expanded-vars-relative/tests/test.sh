#!/usr/bin/env bash
# Standard test harness: runs pytest, writes binary reward to
# /logs/verifier/reward.txt based on pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit status: $status"
echo "reward: $(cat /logs/verifier/reward.txt)"
