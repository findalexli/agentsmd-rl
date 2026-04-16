#!/bin/bash
set -e

# Install pytest and dependencies (using --break-system-packages for container)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests and capture output
if python3 -m pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest_output.txt 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

cat /logs/verifier/pytest_output.txt
