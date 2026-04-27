#!/usr/bin/env bash
# Standardized test runner. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python -m pytest -v \
    --tb=short \
    -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
