#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

# Run the pytest suite. Pytest is already installed in the image (Dockerfile);
# we do NOT pip install at test time.
cd /tests
python3 -m pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    test_outputs.py
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (placeholder block — the harness's standalone_judge.py is invoked by the
#  outer evaluator if this file exists; we intentionally do not exit early.)
true
