#!/bin/bash
# Install pytest if not already installed
pip install pytest --quiet 2>/dev/null || pip install pytest --quiet

# Determine the tests directory
if [ -d "/workspace/task/tests" ]; then
    TESTS_DIR="/workspace/task/tests"
elif [ -d "/tests" ]; then
    TESTS_DIR="/tests"
else
    echo "Cannot find tests directory"
    exit 1
fi

# Run the test file
cd "$TESTS_DIR"
python -m pytest test_outputs.py -v

# Write binary reward based on test results (use .txt extension)
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
