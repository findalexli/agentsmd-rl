#!/bin/bash
# Standardized verifier — DO NOT add task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v --tb=short --color=no \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no rubric judge run here; harness handles rubric scoring separately)

exit 0
