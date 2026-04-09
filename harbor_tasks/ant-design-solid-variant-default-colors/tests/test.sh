#!/bin/bash
set -e

echo "Setting up test environment..."

# Install pytest
pip install pytest --quiet

# Run the tests
echo "Running tests..."
cd /workspace/task

# Run pytest and capture output
python3 -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo "{\"reward\": 1, "success": true}" > /logs/verifier/reward.json
    echo "All tests passed!"
else
    echo "{\"reward\": 0, "success": false}" > /logs/verifier/reward.json
    echo "Some tests failed."
fi

exit $exit_code
