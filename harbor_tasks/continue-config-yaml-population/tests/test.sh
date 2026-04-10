#!/bin/bash
set -e

cd /workspace/continue

# Install pytest if not already available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward
else
    echo "0.0" > /logs/verifier/reward
fi
