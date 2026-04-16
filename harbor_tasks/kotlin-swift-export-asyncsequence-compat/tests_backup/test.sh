#!/bin/bash
set -e

# Install pytest if not available
if ! command -v pytest &> /dev/null; then
    pip3 install pytest -q
fi

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture results
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi
