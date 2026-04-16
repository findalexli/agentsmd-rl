#!/bin/bash

pytest /tests/test_outputs.py -v --tb=short
PYTEST_RC=$?

# Write binary reward: 1 if all tests passed, 0 if any failed
if [ $PYTEST_RC -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
exit $PYTEST_RC