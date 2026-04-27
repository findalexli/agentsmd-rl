#!/usr/bin/env bash
# Run pytest against the oracle test file. Reward is the literal pytest exit
# code: 0 means at least one test failed; 1 means all green.
set -uo pipefail

mkdir -p /logs/verifier

# Run pytest. Use --tb=short so any failure is readable in the harness logs.
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Pytest exit code: $PYTEST_EXIT"
echo "Reward: $(cat /logs/verifier/reward.txt)"
