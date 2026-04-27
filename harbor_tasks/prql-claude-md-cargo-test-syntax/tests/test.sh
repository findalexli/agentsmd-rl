#!/usr/bin/env bash
# Standard task verifier: runs pytest, writes binary reward to /logs/verifier/reward.txt
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest \
    -v \
    --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py \
    | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
