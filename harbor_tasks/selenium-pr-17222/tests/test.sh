#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --quiet --disable-pip-version-check 2>/dev/null || true

# Run tests and capture result
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_RESULT
