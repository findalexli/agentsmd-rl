#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Create virtual environment if it doesn't exist
if [ ! -d "/tmp/venv" ]; then
    python3 -m venv /tmp/venv
    /tmp/venv/bin/pip install pytest
fi

# Run pytest and capture output
/tmp/venv/bin/pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/pytest.log

# Exit with pytest exit code
exit_code=${PIPESTATUS[0]}

# Write reward based on test result
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
