#!/bin/bash
# Standardized test runner. Writes 0 or 1 to /logs/verifier/reward.txt
# from pytest's exit code. No grep-gating, no early exit.
set -u

mkdir -p /logs/verifier

cd /workspace/effect

# pytest and pytest-json-ctrf are baked into the image at build time.
pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    /tests/test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no-op; rubric is evaluated externally from eval_manifest.yaml)
