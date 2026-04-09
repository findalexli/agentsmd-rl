#!/bin/bash

# Install pytest if needed
pip3 install --break-system-packages pytest pyyaml -q 2>/dev/null || pip3 install pytest pyyaml -q

# Run the Python test suite and capture result
python3 -m pytest /tests/test_outputs.py -v --tb=short
TEST_EXIT=$?

# Write binary reward
mkdir -p /logs/verifier
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT
