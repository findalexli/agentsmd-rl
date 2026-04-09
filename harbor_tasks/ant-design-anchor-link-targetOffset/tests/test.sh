#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests and capture output
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write binary reward based on test result
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
