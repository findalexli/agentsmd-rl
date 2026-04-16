#!/bin/bash

cd /workspace

# Install pytest
pip install pytest pyyaml -q

# Run tests
pytest /tests/test_outputs.py -v --tb=short

# Write reward
if [ $? -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
