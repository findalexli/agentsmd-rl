#!/bin/bash
set -e

# Install pytest (use --break-system-packages for Debian 12)
echo "Installing pytest..."
pip3 install pytest --break-system-packages --quiet || pip3 install pytest --quiet

# Run the test file
echo "Running tests..."
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
fi
