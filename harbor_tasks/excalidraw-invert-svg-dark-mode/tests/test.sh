#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check if all tests passed
if grep -q "PASSED" /logs/verifier/test_output.log && ! grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "All tests passed!"
    echo '{"passed": true, "score": 1.0}' > /logs/verifier/results.json
    exit 0
else
    echo "Some tests failed!"
    echo '{"passed": false, "score": 0.0}' > /logs/verifier/results.json
    exit 1
fi
