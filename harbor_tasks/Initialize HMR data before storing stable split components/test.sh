#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Copy test file to writable location in container (in case we need to use a modified version)
# Use the modified version from /task if available (test_outputs.py in root of task)
if [ -f /task/test_outputs.py ]; then
    cp /task/test_outputs.py /tmp/test_outputs.py
    chmod 666 /tmp/test_outputs.py
    TEST_FILE=/tmp/test_outputs.py
else
    TEST_FILE=/tests/test_outputs.py
fi

# Run the tests
python3 -m pytest $TEST_FILE -v 2>&1 | tee /logs/verifier/test_output.log

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
