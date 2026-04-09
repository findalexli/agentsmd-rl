#!/bin/bash
set -e

# Install pytest if needed
pip3 install --quiet pytest pyyaml 2>/dev/null || true

# Run tests
if python3 -m pytest /tests/test_outputs.py -v --tb=no -q 2>&1 | grep -q "passed"; then
    # Check if all tests passed (no failures)
    if python3 -m pytest /tests/test_outputs.py --tb=no -q 2>&1 | grep -E "^(PASSED|ERROR|FAILED).*test_" | grep -qv "PASSED"; then
        # There are failures
        echo "0" > /logs/verifier/reward.txt
    else
        # All tests passed
        echo "1" > /logs/verifier/reward.txt
    fi
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
