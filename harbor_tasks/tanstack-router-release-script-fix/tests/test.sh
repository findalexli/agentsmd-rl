#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Write reward file based on test results
if python3 -m pytest /tests/test_outputs.py -v; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
