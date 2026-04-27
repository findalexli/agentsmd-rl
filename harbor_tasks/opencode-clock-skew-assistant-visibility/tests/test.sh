#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short --ctrf /logs/verifier/ctrf.json test_outputs.py
PY_RC=$?

if [ $PY_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit: $PY_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
