#!/bin/bash
set -e

echo "Setting up Python environment..."
python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || python3 -m pip install pytest --quiet

echo "Running tests..."
# Determine the test directory (handle both mounted /tests and local /workspace/task/tests)
if [ -f /tests/test_outputs.py ]; then
    TEST_DIR=/tests
elif [ -f /workspace/task/tests/test_outputs.py ]; then
    TEST_DIR=/workspace/task/tests
else
    echo "Cannot find test_outputs.py"
    exit 1
fi

# Run pytest and capture results
if python3 -m pytest "$TEST_DIR/test_outputs.py" -v --tb=short 2>&1 | tee /logs/verifier/test_output.log; then
    echo "Tests completed successfully"
    echo '{"passed": true}' > /logs/verifier/result.json
else
    echo "Tests failed"
    echo '{"passed": false}' > /logs/verifier/result.json
fi
