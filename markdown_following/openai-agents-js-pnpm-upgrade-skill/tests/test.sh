#!/usr/bin/env bash
set -euo pipefail

cp /tests/test_outputs.py /tmp/test_outputs.py
cd /tmp

set +e
python3 -m pytest /tmp/test_outputs.py -v --tb=short --junitxml=/logs/verifier/ctrf.json
PYTEST_EXIT=$?
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
echo "tests ran, reward written to /logs/verifier/reward.txt"
