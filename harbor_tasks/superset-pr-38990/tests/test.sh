#!/bin/bash
set -e

# Install pytest if needed
pip install -q pytest

# Run the tests
python -m pytest /workspace/tests/test_outputs.py -v --tb=short

# Write binary reward based on test results
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
