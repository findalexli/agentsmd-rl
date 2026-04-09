#!/bin/bash
set -e

# Install pytest if needed
pip install pytest --quiet 2>/dev/null || true

# Run the tests and capture output
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward: 1 if all tests pass, 0 otherwise
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

exit $exit_code
