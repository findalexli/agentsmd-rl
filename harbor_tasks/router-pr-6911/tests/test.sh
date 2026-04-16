#!/bin/bash
set -euo pipefail

# Install pytest if not available
python3 -m pip install --quiet pytest 2>/dev/null || true

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
