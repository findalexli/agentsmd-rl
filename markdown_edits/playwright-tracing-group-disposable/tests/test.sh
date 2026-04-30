#!/bin/bash
set -e

# Create logs directory if needed
mkdir -p /logs/verifier

# Set up Python environment
if [ ! -d /tmp/venv ]; then
    uv venv /tmp/venv --python=python3
fi
source /tmp/venv/bin/activate

# Install pytest if needed
uv pip install pytest --quiet

# Run the pytest tests
cd /tests
python -m pytest test_outputs.py -v --tb=short
REWARD=$?

# Write reward to the expected location
if [ $REWARD -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
