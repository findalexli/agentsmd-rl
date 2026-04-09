#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run the tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 = fail, 1 = pass)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed."
else
    echo "0" > /logs/verifier/reward
    echo "Tests failed."
    exit 1
fi
