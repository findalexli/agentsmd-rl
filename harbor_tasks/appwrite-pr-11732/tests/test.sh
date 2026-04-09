#!/bin/bash
set -e

# Install pytest if needed
pip install pytest pyyaml 2>/dev/null || true

# Run the verifier tests
cd /workspace
python -m pytest tests/test_outputs.py -v --tb=short

# Write binary reward for the harness
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
