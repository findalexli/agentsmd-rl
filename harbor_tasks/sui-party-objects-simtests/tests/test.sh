#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest -q --break-system-packages 2>/dev/null || pip3 install pytest -q

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward: 1 if all tests pass, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
