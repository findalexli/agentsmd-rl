#!/usr/bin/env bash
# Standardized test harness — DO NOT MODIFY task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

# Run the test suite. Reward is taken directly from pytest's exit code.
cd /tmp
python -m pytest /tests/test_outputs.py \
    -v \
    --tb=short \
    -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (config-edit semantic comparison) is handled by the harbor
# evaluator using eval_manifest.yaml.config_edits; nothing to do here.

exit 0
