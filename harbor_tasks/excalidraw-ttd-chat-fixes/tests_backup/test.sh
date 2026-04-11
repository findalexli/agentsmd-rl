#!/bin/bash
set -e

# Install pytest using --break-system-packages or use virtual environment
pip3 install pytest --quiet --break-system-packages 2>/dev/null || \
    (python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pytest --quiet && \
     export PATH="/tmp/venv/bin:$PATH")

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
