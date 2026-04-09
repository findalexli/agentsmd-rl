#!/bin/bash
set -e

# Standard test.sh for pytest-based verification

cd /workspace

# Install pytest (if not already installed)
pip install pytest --quiet

# Run the test file
pytest /workspace/task/tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward based on test result
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "PASS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAIL: Some tests failed"
fi

exit $EXIT_CODE
