#!/bin/bash
set -e

# Install pytest with system packages override (Docker container environment)
pip install pytest -q --break-system-packages 2>/dev/null

# Run tests from the mounted /tests directory
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Calculate reward: 1 if all tests pass, 0 if any fail
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Return success regardless of test results (we only care about reward)
exit 0
