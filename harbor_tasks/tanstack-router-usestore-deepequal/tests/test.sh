#!/bin/bash
set -e

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test suite
cd /workspace/task/tests
pytest test_outputs.py -v --tb=short

# Write binary reward (exit code determines pass/fail)
exit $?
