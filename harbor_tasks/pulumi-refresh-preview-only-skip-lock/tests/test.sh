#!/usr/bin/env bash
# Test harness for pulumi-refresh-preview-only-skip-lock task.
#
# Runs pytest on /tests/test_outputs.py and writes a binary reward (0|1) to
# /logs/verifier/reward.txt. The reward is taken directly from pytest's
# exit code — do not parse output or add fall-through behaviour, the
# scaffolding rubric `reward_is_pure_pytest` requires this.

set -u

mkdir -p /logs/verifier

cd /tests || exit 1

python3 -m pytest test_outputs.py -v --tb=short --no-header
EXIT=$?

if [ "$EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional judge invocation for this task — pytest is sufficient.)

exit "$EXIT"
