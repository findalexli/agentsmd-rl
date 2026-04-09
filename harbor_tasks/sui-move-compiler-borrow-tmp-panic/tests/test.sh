#!/bin/bash
set -e

# Create virtual environment for pytest
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate

# Install pytest if needed
pip install pytest --quiet

# Run the tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check if all tests passed
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
