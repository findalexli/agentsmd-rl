#!/bin/bash
set -e

# Install pytest
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --break-system-packages || pip install pytest

# Create logs directory
mkdir -p /logs/verifier

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward based on test result
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

exit $exit_code
