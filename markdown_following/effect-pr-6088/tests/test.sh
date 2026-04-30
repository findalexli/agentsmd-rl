#!/bin/bash
set -uo pipefail

cd /workspace/effect

pip install --break-system-packages pytest==8.3.4 2>&1 | tail -1

python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tail -40

if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (reserved for future use)
