#!/bin/bash
set -e

cd /workspace/task/tests

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
pytest test_outputs.py -v --tb=short 2>&1

# Write binary reward based on test results
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed"
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Tests failed"
fi

exit $exit_code
