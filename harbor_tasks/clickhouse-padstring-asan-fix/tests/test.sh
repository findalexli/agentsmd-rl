#!/bin/bash
set -e

# Standard test runner - do not modify

echo "=== Installing pytest ==="
pip3 install pytest -q

echo "=== Running tests ==="
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract results and write reward file
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "=== All tests passed ==="
else
    echo "0" > /logs/verifier/reward
    echo "=== Some tests failed ==="
fi

exit $EXIT_CODE
