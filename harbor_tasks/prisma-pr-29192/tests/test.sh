#!/bin/bash

cd /workspace

pip3 install pytest --break-system-packages --quiet 2>/dev/null || pip3 install pytest --quiet 2>/dev/null

python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1

PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT
