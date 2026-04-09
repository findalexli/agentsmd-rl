#!/bin/bash
set -e

# Install pytest if not present
pip install pytest pytest-mock -q

# Run the test file
cd /workspace
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Extract overall result
if grep -q "passed" /logs/verifier/pytest.log && ! grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "{\"status\": \"success\"}" > /logs/verifier/reward.json
else
    echo "{\"status\": \"failure\"}" > /logs/verifier/reward.json
fi
