#!/bin/bash
set -e

cd /workspace/superset

# Install pytest if not available
pip install pytest --quiet

# Run the test file
cd /workspace/task
python -m pytest tests/test_outputs.py -v || python tests/test_outputs.py

# Write binary reward
mkdir -p /logs/verifier
if [ $? -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "0.0" > /logs/verifier/reward.txt
fi
