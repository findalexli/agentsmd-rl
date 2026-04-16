#!/bin/bash
set -e

# Ensure pytest is available (use --break-system-packages since we're in a container)
pip install pytest --quiet --break-system-packages 2>/dev/null || pip install pytest --quiet 2>/dev/null || true

# Run the test suite and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Check if all tests passed
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
