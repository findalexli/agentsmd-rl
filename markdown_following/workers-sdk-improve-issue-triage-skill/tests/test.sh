#!/usr/bin/env bash
# Standard pytest runner. Reward is binary: 1 iff every test in
# /tests/test_outputs.py passes; 0 otherwise. Reward comes from pytest's
# exit code only — no grep on output.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

cat /logs/verifier/pytest.log

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "test.sh: pytest_rc=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"
