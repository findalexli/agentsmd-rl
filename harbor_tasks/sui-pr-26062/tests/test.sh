#!/bin/bash

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run the tests and capture exit code
cd /workspace/sui
pytest /tests/test_outputs.py -v --tb=short
EXIT_CODE=$?

# Write binary reward
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
