#!/bin/bash
set -o pipefail

# Install pytest if not present
pip install pytest pytest-asyncio -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests with correct PYTHONPATH
cd /workspace/openhands
export PYTHONPATH="/workspace/openhands:/workspace/openhands/enterprise:$PYTHONPATH"

# Run pytest and capture exit code
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log
exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
