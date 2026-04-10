#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q

# Determine reward based on test results
# Check if all fail-to-pass tests passed
REWARD=0

# Check runtime_exception_not_wrapped - this test should pass (pytest PASSED)
# and the inner test should report success
if pytest /tests/test_outputs.py::test_runtime_exception_not_wrapped -v 2>&1 | grep -q "::test_runtime_exception_not_wrapped PASSED"; then
    # Check various_runtime_exceptions
    if pytest /tests/test_outputs.py::test_various_runtime_exceptions -v 2>&1 | grep -q "::test_various_runtime_exceptions PASSED"; then
        REWARD=1
    fi
fi

# Write binary reward
echo "$REWARD" > /logs/verifier/reward.txt
echo "Reward: $REWARD"
