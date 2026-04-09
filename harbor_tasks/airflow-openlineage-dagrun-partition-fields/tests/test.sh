#!/bin/bash
set -e

# Install pytest
pip install pytest --quiet

# Create logs directory
mkdir -p /logs/verifier

# Run the tests
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
exit_code=${PIPESTATUS[0]}

# Write binary reward
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
