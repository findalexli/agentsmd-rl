#!/bin/bash

# Install pytest if not already available
pip install pytest --quiet --break-system-packages 2>/dev/null || pip install pytest --quiet

# Run the test file
cd /tests
python3 -m pytest test_outputs.py -v
exit_code=$?

# Write binary reward file (1 if all passed, 0 otherwise)
mkdir -p /logs/verifier
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
