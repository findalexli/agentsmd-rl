#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture output (pipefail ensures we catch test failures)
set -o pipefail
if pytest /tests/test_outputs.py -v --tb=short -o cache_dir=/tmp/pytest_cache 2>&1 | tee /logs/verifier/pytest_output.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
