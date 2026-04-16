#!/bin/bash

# Install pytest if needed (use --break-system-packages for Debian-based containers)
pip3 install pytest --quiet --break-system-packages || pip3 install pytest --quiet

# Run the tests and capture exit code
cd /tests
python3 -m pytest test_outputs.py -v --tb=short
PYTEST_EXIT=$?

# Write binary reward (1 if all tests passed, 0 otherwise)
if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
