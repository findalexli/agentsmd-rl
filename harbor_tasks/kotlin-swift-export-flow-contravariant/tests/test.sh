#!/bin/bash
set -e

# Install pytest if not available
python3 -m pip install pytest -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run the tests and capture output
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short > /logs/verifier/pytest.log 2>&1; then
    # All tests passed - write reward 1
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
    cat /logs/verifier/pytest.log
    exit 0
else
    # Some tests failed - write reward 0
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
    cat /logs/verifier/pytest.log
    exit 0
fi
