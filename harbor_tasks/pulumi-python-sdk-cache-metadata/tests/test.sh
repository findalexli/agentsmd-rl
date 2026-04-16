#!/bin/bash
set -e

# Install pytest
pip install pytest --quiet

# Create logs directory
mkdir -p /logs/verifier

# Run the tests
cd /workspace/pulumi/sdk/python
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Check exit code and write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
