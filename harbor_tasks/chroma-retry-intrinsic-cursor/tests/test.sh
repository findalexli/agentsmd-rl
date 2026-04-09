#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest --quiet

# Run the test suite
cd /workspace
pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

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
