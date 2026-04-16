#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Install pytest if needed
pip3 install pytest --quiet 2>/dev/null || true

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Extract test results and write binary reward
if grep -q "passed" /logs/verifier/pytest_output.log && ! grep -q "FAILED" /logs/verifier/pytest_output.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1" >> /logs/verifier/pytest_output.log
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0" >> /logs/verifier/pytest_output.log
fi

cat /logs/verifier/reward.txt
