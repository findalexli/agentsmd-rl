#!/bin/bash
# Standard test runner - do not modify

# Install pytest if not present
python3 -m pip install --quiet pytest 2>/dev/null || true

# Run the tests and capture exit code
cd /tests
python3 -m pytest test_outputs.py -v --tb=short
exit_code=$?

# Write binary reward based on exit code
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
