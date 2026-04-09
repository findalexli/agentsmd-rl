#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Copy the regression test file to the frontend tests directory
# This ensures the test is available during test execution
cp /workspace/task/tests/budget-error-regression.test.ts /workspace/openhands/frontend/__tests__/

# Run the Python test suite that orchestrates the vitest tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract the test result
EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward file (1 = all passed, 0 = any failed)
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $EXIT_CODE
