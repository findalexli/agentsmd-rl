#!/bin/bash

# Install pytest if needed
pip install pytest --quiet --break-system-packages

# Run tests directly (tests are mounted at /tests)
cd /

# Run pytest and capture exit code to temp file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log; echo ${PIPESTATUS[0]} > /tmp/exit_code

# Read exit code
read exit_code < /tmp/exit_code

# Write binary reward
if [ "$exit_code" = "0" ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $exit_code
