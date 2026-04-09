#!/bin/bash
set -e

# Install pytest if needed
pip install pytest --quiet --break-system-packages 2>/dev/null || true

# Run tests and capture output
cd /workspace/openhands
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Check if all tests passed
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
