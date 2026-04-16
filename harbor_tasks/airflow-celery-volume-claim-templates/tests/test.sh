#!/bin/bash
set -e

# Install pytest and dependencies if not already installed
pip install -q pytest pyyaml jmespath jsonschema 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
EXIT_CODE=${PIPESTATUS[0]}

# Write reward file (1 if all tests passed, 0 otherwise)
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

exit $EXIT_CODE
