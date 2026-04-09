#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages

# Run tests and capture output
cd /tests
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file (1 = all passed, 0 = any failed)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward
    echo "FAILURE: Some tests failed"
    exit 1
fi
