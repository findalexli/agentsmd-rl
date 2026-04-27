#!/bin/bash
# Standardized test runner: runs pytest on /tests/test_outputs.py and
# writes binary reward (0/1) to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

# pytest is already installed in the Docker image.
cd /tests
python3 -m pytest -v --tb=short test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_RC"
echo "reward=$(cat /logs/verifier/reward.txt)"
