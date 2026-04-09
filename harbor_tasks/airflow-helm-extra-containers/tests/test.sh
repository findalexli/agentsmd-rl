#!/bin/bash
set -e

LOGS_DIR="/logs/verifier"
mkdir -p "$LOGS_DIR"

# Install pytest and dependencies if not already installed
pip install -q pytest pyyaml jmespath jsonschema

# Run the tests
cd /workspace/task
pytest tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOGS_DIR/test_output.log"

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > "$LOGS_DIR/reward"
    echo "All tests passed!"
else
    echo "0" > "$LOGS_DIR/reward"
    echo "Some tests failed."
    exit 1
fi
