#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest -q --break-system-packages 2>/dev/null || true

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward based on test results
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
