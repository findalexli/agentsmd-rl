#!/usr/bin/env bash
# Standardized harness: pytest exit-code → /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_EXIT"
echo "reward: $(cat /logs/verifier/reward.txt)"
