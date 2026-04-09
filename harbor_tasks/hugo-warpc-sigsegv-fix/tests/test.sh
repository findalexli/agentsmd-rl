#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short

# Write binary reward (1 for success, 0 for failure)
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
