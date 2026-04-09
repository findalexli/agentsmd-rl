#!/bin/bash

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests - always write reward at the end
cd /workspace/sui
python3 -m pytest /tests/test_outputs.py -v --tb=short
EXIT_CODE=$?

# Write binary reward to the verifier log
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
