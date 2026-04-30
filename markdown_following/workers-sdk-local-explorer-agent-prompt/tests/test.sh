#!/bin/bash
set -euo pipefail

# Install test dependencies
pip3 install pytest==8.3.4 --break-system-packages -q

# Run pytest and write binary reward from exit code
cd /tests
set +e
python3 -m pytest test_outputs.py -v --tb=short 2>&1
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Placeholder for future LLM judge integration
echo "Judge: skipped (code_fix task, no semantic diff needed)"

exit 0
