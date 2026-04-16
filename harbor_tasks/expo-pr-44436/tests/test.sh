#!/bin/bash
set -e

apt-get update -qq && apt-get install -y -qq python3 python3-pip > /dev/null 2>&1

pip install pytest -q

# Run tests and capture exit code
set +e
pytest /tests/test_outputs.py -v --tb=short
TEST_EXIT_CODE=$?
set -e

# Write binary reward: pytest exit code 0 → reward 1 (pass)
#                      pytest exit code non-0 → reward 0 (fail)
if [ "$TEST_EXIT_CODE" = "0" ]; then
    echo -n "1" > /logs/verifier/reward.txt
    echo "Reward: 1 (PASS)"
else
    echo -n "0" > /logs/verifier/reward.txt
    echo "Reward: 0 (FAIL)"
    exit 1
fi