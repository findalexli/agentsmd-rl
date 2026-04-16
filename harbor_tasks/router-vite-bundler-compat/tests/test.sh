#!/bin/bash
set -e

# Install pytest
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests and capture results
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward (1 if all passed, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
