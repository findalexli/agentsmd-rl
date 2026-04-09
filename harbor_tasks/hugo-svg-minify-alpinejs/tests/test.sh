#!/bin/bash
set -e

echo "Installing pytest..."
pip install pytest --quiet

echo "Running tests..."
cd /workspace/task
cp tests/test_outputs.py /workspace/test_outputs.py

# Run pytest and capture results
pytest /workspace/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward signal (0 = fail, 1 = pass)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/signal
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/signal
    echo "Some tests failed."
    exit 1
fi
