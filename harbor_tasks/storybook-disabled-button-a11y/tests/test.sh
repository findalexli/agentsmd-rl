#!/bin/bash
set -e

# Install pytest if needed
pip install pytest --quiet 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run the test file
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward
if grep -q "passed" /logs/verifier/pytest.log && ! grep -q "failed" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
