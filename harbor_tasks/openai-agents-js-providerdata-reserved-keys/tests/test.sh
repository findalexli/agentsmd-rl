#!/usr/bin/env bash
# Standardised verifier harness — runs pytest, writes binary reward.
set -uo pipefail

mkdir -p /logs/verifier

# pytest and the ctrf reporter are pre-installed in the Dockerfile.
cd /tests

python3 -m pytest \
    -v \
    --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (Soft-rule rubric evaluation is performed externally by the harness.)

exit 0
