#!/bin/bash

pip3 install --break-system-packages pytest pytest-timeout pytest-xdist pytest-mock

python3 -m pytest /tests/test_outputs.py -v --tb=short --timeout=300

# reward = 1 if pytest passed (exit 0), reward = 0 if pytest failed (exit != 0)
if [ $? -eq 0 ]; then
    echo -n "1" > /logs/verifier/reward.txt
else
    echo -n "0" > /logs/verifier/reward.txt
fi
