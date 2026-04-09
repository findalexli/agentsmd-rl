#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest pyyaml -q 2>/dev/null || true

# Run the test file
cd /workspace/kotlin
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on pytest result
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
