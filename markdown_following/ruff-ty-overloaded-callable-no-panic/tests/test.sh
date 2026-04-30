#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest \
    -v \
    --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
RC=$?

if [ "$RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
