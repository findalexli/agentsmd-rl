#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Install required dependencies for conftest.py
pip install boto3 -q
pip install /workspace/dagster/python_modules/dagster-test -q 2>/dev/null || true
pip install /workspace/dagster/python_modules/libraries/dagster-postgres -q 2>/dev/null || true

# Install pytest if not already installed
pip install pytest -q

# Run the test suite
cd /workspace/dagster
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward based on test results
REWARD=0
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    # Count total tests passed
    PASSED=$(grep -oP '\d+ passed' /logs/verifier/pytest_output.txt | grep -oP '\d+' || echo "0")
    TOTAL=$(grep -oP '\d+ items' /logs/verifier/pytest_output.txt | grep -oP '\d+' || echo "1")

    # If all tests pass, reward = 1
    if [ "$PASSED" -eq "$TOTAL" ]; then
        REWARD=1
    else
        # Partial reward based on proportion
        REWARD=$(python3 -c "print($PASSED / $TOTAL)")
    fi
fi

# Write reward to file
echo "$REWARD" > /logs/verifier/reward.txt
echo "Tests completed. Reward: $REWARD"
