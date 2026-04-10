#!/bin/bash

# Install pytest if not present
pip install pytest --quiet 2>/dev/null

# Run the tests
cd /workspace/task
echo "Running tests..."
python -m pytest tests/test_outputs.py -v --tb=short
exit_code=$?

# Write binary reward
if [ $exit_code -eq 0 ]; then
    echo "All tests passed!"
    echo '{"reward": 1.0, "status": "passed"}' > /logs/verifier/result.json
else
    echo "Tests failed!"
    echo '{"reward": 0.0, "status": "failed"}' > /logs/verifier/result.json
fi

exit $exit_code
