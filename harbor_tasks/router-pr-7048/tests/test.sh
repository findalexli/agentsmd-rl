#!/bin/bash
set -e

# Install pytest if not available
python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || \
    python3 -m pip install pytest --quiet

# Run tests and capture result
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
