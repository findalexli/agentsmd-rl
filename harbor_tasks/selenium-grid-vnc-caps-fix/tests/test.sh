#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run the verifier tests
cd /workspace/task
python -m pytest tests/test_outputs.py -v --tb=short

# Write binary reward to the expected location
# The test_outputs.py will exit with 0 if all tests pass
if [ $? -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
