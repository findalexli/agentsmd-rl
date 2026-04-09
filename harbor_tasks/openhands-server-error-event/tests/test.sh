#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
if grep -q "PASSED" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
fi
