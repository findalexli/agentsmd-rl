#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier
cd /tests

python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json
EXIT=$?

if [ $EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
