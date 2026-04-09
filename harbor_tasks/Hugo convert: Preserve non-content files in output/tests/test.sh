#!/bin/bash
set -e

# Install pytest if not available
pip install pytest --quiet 2>/dev/null || true

# Run the tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v 2>&1

# Write binary reward signal
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
