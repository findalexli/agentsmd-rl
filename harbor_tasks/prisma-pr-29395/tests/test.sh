#!/bin/bash

pip3 install pytest -q --break-system-packages

cd /workspace

set +e
pytest /tests/test_outputs.py -v --tb=short --no-header -o "pythonpath=."
pytest_exit=$?
set -e

# pytest returns 0 for pass, 1 for fail - invert for reward
if [ $pytest_exit -eq 0 ]; then
    reward=1
else
    reward=0
fi

if [ -d /logs/verifier ]; then
    echo -n "$reward" > /logs/verifier/reward.txt
fi

exit 0
