#!/bin/bash

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test file using pytest module
cd /workspace/sanity
python3 -m pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/test_output.log 2>&1
TEST_EXIT=$?

# Write binary reward based on test results
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/test_output.log
exit $TEST_EXIT
