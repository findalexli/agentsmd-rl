#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture output
if pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

cat /logs/verifier/pytest_output.txt
