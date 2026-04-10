#!/bin/bash
set -e

cd /workspace/dagster

# Install pytest if not already installed
if ! command -v pytest &> /dev/null; then
    pip install pytest
fi

# Run the tests and capture output
pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Tests failed."
    exit 1
fi
