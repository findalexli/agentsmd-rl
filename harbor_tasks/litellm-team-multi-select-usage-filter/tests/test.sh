#!/usr/bin/env bash
# Standardized harness: run pytest, write reward to /logs/verifier/reward.txt
set -u

mkdir -p /logs/verifier

# pytest is preinstalled inside /opt/venv (see Dockerfile); no install at run time.
cd /tests

python -m pytest \
    -p no:cacheprovider \
    --tb=short \
    -v \
    --json-report \
    --json-report-file=/logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Provide unified output for harness debugging.
echo "--- pytest exit status: $status ---"
echo "--- reward: $(cat /logs/verifier/reward.txt) ---"

# --- LLM Judge ---
# (No rubric judge logic at this level — pytest is the sole oracle.)
exit 0
