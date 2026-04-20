#!/bin/bash

python3 -m pytest /tests/test_outputs.py -v --tb=short --timeout-method=thread --timeout=600
RETVAL=$?

# Write binary reward
if [ $RETVAL -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $RETVAL