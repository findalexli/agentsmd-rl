#!/bin/bash
set -e

# Install pytest if not available
pip install pytest pytz croniter -q

# Create logs directory
mkdir -p /logs/verifier

# Run the tests and capture output
if cd /workspace/dagster && python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi
