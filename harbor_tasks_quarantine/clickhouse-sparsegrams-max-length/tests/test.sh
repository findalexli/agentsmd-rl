#!/bin/bash
set -e

# Copy test file to workspace
cp /tests/test_outputs.py /workspace/test_outputs.py

# Install pytest if not available
if ! python3 -c "import pytest" 2>/dev/null; then
    pip3 install pytest -q 2>/dev/null || pip install pytest -q 2>/dev/null || true
fi

# Run the tests
cd /workspace
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
