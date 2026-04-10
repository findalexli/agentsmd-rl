#!/bin/bash

# Install pytest if needed
pip install pytest -q --break-system-packages 2>/dev/null

# Run tests
python3 -m pytest /tests/test_outputs.py -v --tb=short
TEST_RESULT=$?

# Write reward for harness (0 = tests failed, 1 = tests passed)
if [ $TEST_RESULT -eq 0 ]; then
    echo '1' > /logs/verifier/reward.txt
else
    echo '0' > /logs/verifier/reward.txt
fi
