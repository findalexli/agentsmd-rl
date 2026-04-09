#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check if all tests passed
if grep -q "passed" /logs/verifier/test_output.log && ! grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi
