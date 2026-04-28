#!/bin/bash
set -euo pipefail

pip3 install --break-system-packages pytest==8.3.4 2>&1

python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# This block is for LLM-based evaluation of config edits.
# It runs after the pytest verdict and does not affect reward.txt.
