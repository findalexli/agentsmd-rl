#!/bin/bash
set -e

cd /workspace/excalidraw

# Install pytest if not already installed
pip3 install pytest --quiet --break-system-packages || pip3 install pytest --quiet || true

# Run the test suite
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
TEST_EXIT_CODE=${PIPESTATUS[0]}

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

exit $TEST_EXIT_CODE
