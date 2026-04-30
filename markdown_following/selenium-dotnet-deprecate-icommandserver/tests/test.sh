#!/usr/bin/env bash
# Run the behavioral tests for this task and write a binary reward to
# /logs/verifier/reward.txt. The reward MUST come straight from pytest's exit
# code (rubric: reward_is_pure_pytest).
set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v \
    --tb=short \
    --ctrf=/logs/verifier/ctrf.json
rc=$?

if [ $rc -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$rc, reward=$(cat /logs/verifier/reward.txt)"
exit $rc
