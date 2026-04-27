#!/usr/bin/env bash
# Standardised reward harness — DO NOT edit task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest.log
echo "---"
echo "reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge (Track 2 — markdown_authoring) ---
# Track 2 evaluation runs out-of-band by harbor's judge; nothing else to do here.

exit 0
