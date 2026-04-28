#!/bin/bash
set -euo pipefail

pip3 install pytest==8.3.4 --break-system-packages --quiet 2>&1 || { echo "ERROR: failed to install pytest"; exit 1; }

cd /tests
set +e
python3 -m pytest test_outputs.py -v --tb=short 2>&1
RET=$?
set -e
if [ $RET -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Judge placeholder — this block is reached; the judge populates it at eval time.
