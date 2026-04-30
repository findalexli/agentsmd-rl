#!/usr/bin/env bash
# Standardized test runner. Do not modify.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short test_outputs.py | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
