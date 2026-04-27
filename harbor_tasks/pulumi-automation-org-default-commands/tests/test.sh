#!/bin/bash
# Standardized test runner. Reward is pure-pytest exit code.
set -u

mkdir -p /logs/verifier

# Pytest is preinstalled in the Docker image; do not install at test time.
cd /workspace || exit 1

python3 -m pytest /tests/test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_EXIT"
echo "reward: $(cat /logs/verifier/reward.txt)"
