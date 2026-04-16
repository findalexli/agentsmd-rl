#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test suite
cd /tests
set +e
pytest test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1
REWARD=$?
set -e

# Write binary reward
if [ $REWARD -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest_output.txt
echo "Exit code: $REWARD"
