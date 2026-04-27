#!/bin/bash
# Standardised test runner. Reward is the literal '0' or '1', written to
# /logs/verifier/reward.txt directly from pytest's exit code.
set -u

mkdir -p /logs/verifier

cd /workspace/superset

# Run pytest. The task's own checks live in /tests/test_outputs.py; the
# conftest.py inside /workspace/superset stubs the heavy superset package init.
python -m pytest -v --tb=short -p no:cacheprovider /tests/test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No judge for this task; rubric runs out-of-band against agent diff.)

exit 0
