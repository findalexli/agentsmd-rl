#!/bin/bash

# Install pytest if not already available
pip install pytest -q

# Run the test suite and capture output and exit code
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log
exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 1
fi
