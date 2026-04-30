#!/usr/bin/env bash
# Standardized test runner. Writes pytest exit code as binary reward to
# /logs/verifier/reward.txt. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests || exit 1

# Use the venv pytest installed in the Dockerfile. No installs at test time.
export PATH="/opt/venv/bin:$PATH"

pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit: $PYTEST_EXIT"
echo "reward: $(cat /logs/verifier/reward.txt)"
