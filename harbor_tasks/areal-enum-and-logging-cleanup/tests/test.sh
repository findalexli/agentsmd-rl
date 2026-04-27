#!/usr/bin/env bash
# Standard test runner. Do NOT add task-specific logic here.
set -u

mkdir -p /logs/verifier

# Run pytest. Capture full output for debugging.
cd /tests
python -m pytest test_outputs.py -v --tb=short --json-report --json-report-file=/logs/verifier/ctrf.json 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Pytest exit: $PYTEST_RC"
echo "Reward: $(cat /logs/verifier/reward.txt)"

exit 0
