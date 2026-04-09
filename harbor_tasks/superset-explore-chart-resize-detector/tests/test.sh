#!/bin/bash
set -e

echo "Setting up test environment..."

# Install pytest if not present
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests
echo "Running tests..."
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi

exit $EXIT_CODE
