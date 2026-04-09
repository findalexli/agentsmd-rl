#!/bin/bash
set -e

# Install Python dependencies if not already installed
pip3 install --break-system-packages -q pytest pyyaml 2>/dev/null || true

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward: 1 if all tests pass, 0 otherwise
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $EXIT_CODE
