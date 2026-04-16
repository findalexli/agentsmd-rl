#!/bin/bash
# Standard test runner for benchmark tasks
set -e

# Install pytest if not present
python3 -m pip install --quiet --break-system-packages pytest 2>/dev/null || true

# Run tests and capture result
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
