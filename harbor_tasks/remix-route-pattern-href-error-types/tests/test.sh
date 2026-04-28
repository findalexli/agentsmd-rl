#!/bin/bash
set -uo pipefail

# --- pytest harness ---
pip3 install pytest==8.3.4 --break-system-packages --quiet

cd /tests

python3 -m pytest -v --tb=short test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

# --- reward ---
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
echo "LLM judge placeholder"
