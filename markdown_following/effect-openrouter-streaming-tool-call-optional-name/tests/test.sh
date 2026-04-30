#!/bin/bash
# Runs pytest, writes binary reward to /logs/verifier/reward.txt.

set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    --tb=short \
    -v \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit $PYTEST_RC
