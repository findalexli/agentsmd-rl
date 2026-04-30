#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/remix

# Run the oracle tests via pytest. Reward is purely the pytest exit code.
pytest \
    --tb=short \
    -v \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
