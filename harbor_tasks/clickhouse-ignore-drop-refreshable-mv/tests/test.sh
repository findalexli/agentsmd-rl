#!/bin/bash
set -e

# Install pytest if needed (use --break-system-packages for Ubuntu 24.04)
pip install pytest --break-system-packages -q 2>/dev/null || true

# Run tests
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward based on test results
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "failed" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
