#!/usr/bin/env bash
# Standardized verifier entrypoint. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (none configured for this task)

exit 0
