#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the tests
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v --tb=short

# Write reward file (1 for success)
mkdir -p /logs/verifier
echo "1" > /logs/verifier/reward

echo "All tests passed!"
