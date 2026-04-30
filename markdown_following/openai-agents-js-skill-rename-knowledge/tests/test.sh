#!/usr/bin/env bash
set -eu

# Run test_outputs.py
# (pytest and pyyaml are pre-installed in the Docker image)
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
rc=${PIPESTATUS[0]}

# Write binary reward from exit code
if [ $rc -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
echo "Judge block placeholder"
