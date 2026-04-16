#!/bin/bash
set -e

# Install pytest if needed
python3 -c "import pytest" 2>/dev/null || pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
cd /workspace/lancedb
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write reward file (1 if all tests passed, 0 otherwise)
if grep -q "passed" /logs/verifier/test_output.log && ! grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
