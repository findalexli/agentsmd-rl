#!/bin/bash
# Standard task test harness.
# Runs pytest on /tests/test_outputs.py and writes binary reward to /logs/verifier/reward.txt.

set -uo pipefail

mkdir -p /logs/verifier

# pytest and pytest-json-report are pre-installed in the Dockerfile;
# no network access is performed at test time.

cd /tests

python3 -m pytest test_outputs.py \
    -v \
    --tb=short \
    --json-report \
    --json-report-file=/logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (No additional rubric judging needed for this task — reward is purely
# pytest-driven. Block kept for compatibility with harness expectations.)
exit 0
