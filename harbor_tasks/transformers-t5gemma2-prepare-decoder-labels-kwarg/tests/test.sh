#!/usr/bin/env bash
# Standardized boilerplate. DO NOT add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

# Pytest is installed in the Dockerfile.
python -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
