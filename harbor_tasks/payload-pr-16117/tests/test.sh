#!/bin/bash
set -e

cd /workspace/payload

python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1

PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo -n "1" > /logs/verifier/reward.txt
else
    echo -n "0" > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT