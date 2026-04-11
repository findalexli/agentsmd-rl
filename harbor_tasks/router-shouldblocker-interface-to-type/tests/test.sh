#!/bin/bash
set -o pipefail

# Install pytest
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward
REWARD=$?
if [ $REWARD -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $REWARD
