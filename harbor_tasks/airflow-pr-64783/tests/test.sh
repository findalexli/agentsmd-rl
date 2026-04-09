#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q

# Run the tests in a temp directory to avoid picking up repo's pyproject.toml
# The tests use absolute paths to find the target file
cd /tmp
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check if tests passed
exit_code=${PIPESTATUS[0]}

# Write binary reward
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
