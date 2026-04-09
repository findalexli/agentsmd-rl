#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file
TEST_EXIT_CODE=${PIPESTATUS[0]}
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed!"
fi

exit $TEST_EXIT_CODE
