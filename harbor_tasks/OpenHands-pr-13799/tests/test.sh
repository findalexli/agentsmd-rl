#!/bin/bash
set -e

# Install pytest and dependencies if not already installed
pip install -q pytest httpx 2>/dev/null || true

# Run the test suite and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward: 1 if all tests pass, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

# Return success to prevent Docker from failing even when tests fail
exit 0
