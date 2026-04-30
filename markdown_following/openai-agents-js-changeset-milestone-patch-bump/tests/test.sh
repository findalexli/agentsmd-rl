#!/usr/bin/env bash
# Standardized test harness — runs pytest and writes binary reward.
set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py \
    > /logs/verifier/pytest.log 2>&1
RC=$?

cat /logs/verifier/pytest.log

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "reward: $(cat /logs/verifier/reward.txt)"
