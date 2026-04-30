#!/usr/bin/env bash
# Standardised pytest runner — produces /logs/verifier/reward.txt with literal "0" or "1".
set -u

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short > /logs/verifier/pytest.log 2>&1
EXIT=$?

cat /logs/verifier/pytest.log

if [ "$EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
