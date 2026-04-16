#!/bin/bash

# Install pytest if needed
pip install pytest -q 2>/dev/null || true

# Run the tests
cd /tests
pytest test_outputs.py -v --tb=short
TEST_EXIT=$?

# Write reward file
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT
