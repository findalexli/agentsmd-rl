#!/bin/bash

# Run pytest tests
pip install pytest==8.3.4 -q --break-system-packages
python3 -m pytest /tests/test_outputs.py -v --tb=short

# Write reward
if [ $? -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
