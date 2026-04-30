#!/usr/bin/env bash
# Standardized test runner. Runs pytest against /tests/test_outputs.py
# and writes a literal 0/1 reward to /logs/verifier/reward.txt based on
# pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py \
    > /logs/verifier/pytest.log 2>&1
PYTEST_EXIT=$?

cat /logs/verifier/pytest.log

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] reward=$(cat /logs/verifier/reward.txt)"
