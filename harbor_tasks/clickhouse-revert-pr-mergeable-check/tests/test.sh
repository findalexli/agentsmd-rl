#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q

# Create logs directory
mkdir -p /logs/verifier

# Run tests
cd /workspace/ClickHouse
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests failed - reward=0"
fi
