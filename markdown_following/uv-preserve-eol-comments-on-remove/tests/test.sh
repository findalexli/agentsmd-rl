#!/usr/bin/env bash
# Standardized test runner. Reward = pytest exit code (0|1) at /logs/verifier/reward.txt.
set -u

mkdir -p /logs/verifier

cd /tests

# pytest-json-ctrf produces ctrf.json for the every_gold_test_passes audit.
pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
