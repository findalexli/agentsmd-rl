#!/bin/bash
set -e

cd /workspace/task/tests

# Install pytest if not already installed
pip3 install pytest --quiet

# Run the tests
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi
