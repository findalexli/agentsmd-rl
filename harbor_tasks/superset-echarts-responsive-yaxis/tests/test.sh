#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short test_outputs.py
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT
