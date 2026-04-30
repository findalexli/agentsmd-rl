#!/usr/bin/env bash
# Standardized test runner. Writes binary reward to /logs/verifier/reward.txt
# from pytest's exit code. Do not add task-specific logic here.

set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/mlflow

python -m pytest \
    -v \
    --tb=short \
    --junitxml=/logs/verifier/junit.xml \
    /tests/test_outputs.py
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No-op — rubric judging is performed by the harness from eval_manifest.yaml.)

exit 0
