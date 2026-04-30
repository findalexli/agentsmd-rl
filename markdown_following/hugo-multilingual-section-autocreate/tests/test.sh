#!/bin/bash
# Standardized verifier wrapper. Runs pytest on test_outputs.py and writes
# a binary reward (0 or 1) to /logs/verifier/reward.txt based on the exit
# code. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

# Pytest and its deps are pinned in the Dockerfile; if missing here, the
# environment is broken and we want to surface that loudly (no `|| true`).
python3 -m pytest --version >/dev/null

# Run the verifier tests.
python3 -m pytest /tests/test_outputs.py \
    -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    2>&1 | tee /logs/verifier/pytest_output.txt

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved for downstream rubric evaluation; not invoked here.

exit 0
