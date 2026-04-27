#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short test_outputs.py --ctrf=/logs/verifier/ctrf.json
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
