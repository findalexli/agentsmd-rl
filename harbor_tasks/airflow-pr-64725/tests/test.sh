#!/bin/bash
# Standard test runner for benchmark tasks
set -euo pipefail

# Install pytest if not available
pip install --quiet pytest

# Run the tests
cd /tests
if pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
