#!/bin/bash
# Standardized test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, writes binary reward

set -e

# Install pytest and ruff for linting checks
pip install --quiet pytest ruff

# Run tests and capture exit code
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT_CODE
