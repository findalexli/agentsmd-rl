#!/usr/bin/env bash
# Standardized harness: runs pytest, writes binary reward to /logs/verifier/reward.txt.
set -u
mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_EXIT, reward=$(cat /logs/verifier/reward.txt)"
