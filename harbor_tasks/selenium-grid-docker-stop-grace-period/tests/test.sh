#!/bin/bash
set -e

# Install pytest if needed
python3 -m pip install --quiet pytest 2>/dev/null || true

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests pass, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
  echo "1" > /logs/verifier/reward.txt
else
  echo "0" > /logs/verifier/reward.txt
fi
