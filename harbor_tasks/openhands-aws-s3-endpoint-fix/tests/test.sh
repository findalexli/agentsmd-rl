#!/bin/bash
set -e

# Install pytest if not available
pip install pytest pytest-asyncio -q

# Run tests
cd /tests
python -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (1 if all tests pass, 0 otherwise)
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
