#!/bin/bash
set -e

# Setup log directory
mkdir -p /logs/verifier

# Change to the code directory where tests run
cd /workspace/storybook/code

# Install pytest if not already available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --break-system-packages || true

# Run the test file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Extract reward value (0 or 1 based on test results)
# If pytest passed (exit 0), reward is 1, else 0
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
