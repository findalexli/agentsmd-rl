#!/usr/bin/env bash
# Standard pytest harness: writes 0/1 reward to /logs/verifier/reward.txt
# from pytest's exit code. Do not customise.

set -u
mkdir -p /logs/verifier

cd /tests

python3 -m pytest -v --tb=short test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
