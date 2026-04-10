#!/bin/bash
set -e

cd /tests

# Install pytest
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --user 2>/dev/null || pip3 install pytest

# Run the tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi

exit $exit_code
