#!/bin/bash
# Run all tests using pytest

set -e

cd /workspace/taskforge

# Run the test file with pytest if available, otherwise with python
if python3 -c "import pytest" 2>/dev/null; then
    python3 -m pytest /tests/test_outputs.py -v || TEST_FAILED=1
else
    python3 /tests/test_outputs.py || TEST_FAILED=1
fi

# Write reward file if logs directory exists
if [ -d "/logs/verifier" ]; then
    if [ -z "$TEST_FAILED" ]; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
fi
