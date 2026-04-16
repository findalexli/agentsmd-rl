#!/bin/bash

cd /workspace/continue_repo

# Run pytest on test_outputs.py
python -m pytest /tests/test_outputs.py -v --tb=short
REWARD=$?

if [ $REWARD -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $REWARD
