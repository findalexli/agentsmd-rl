#!/bin/bash

cd /workspace/withastro-astro

# Install pytest if not already installed
pip3 install -q --break-system-packages pytest

# Run the tests
pytest -v --tb=short /tests/test_outputs.py
TEST_RESULT=$?

# Write reward
if [ $TEST_RESULT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi

exit $TEST_RESULT
