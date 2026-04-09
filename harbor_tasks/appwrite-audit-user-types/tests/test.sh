#!/bin/bash
set -e

# Install pytest if needed
pip install pytest pyyaml -q 2>/dev/null || true

# Run the test suite
cd /workspace/appwrite
python3 /workspace/task/appwrite-audit-user-types/tests/test_outputs.py -v

# Write binary reward for each test
# This is handled by pytest exit code - 0 means all passed
if [ $? -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed!"
    exit 1
fi
