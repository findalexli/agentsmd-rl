#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/lancedb

python3 -m pytest /tests/test_outputs.py -v --tb=short \
    > /logs/verifier/pytest_stdout.log 2>&1
PYTEST_RC=$?

cat /logs/verifier/pytest_stdout.log

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
