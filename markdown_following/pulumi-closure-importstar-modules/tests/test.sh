#!/usr/bin/env bash
# Standardized test runner. Computes reward strictly from pytest's exit code.
set -u

mkdir -p /logs/verifier

# pytest and pytest-json-ctrf are installed at image build time.
cd /tests
pytest -v --tb=short --ctrf /logs/verifier/ctrf.json test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Optional rubric judge: runs only if a manifest+judge are present. Errors are
# non-fatal — reward above is authoritative.
if [ -f /tests/eval_manifest.yaml ] && [ -f /tests/standalone_judge.py ]; then
    python3 /tests/standalone_judge.py \
        --manifest /tests/eval_manifest.yaml \
        --repo /workspace/pulumi \
        > /logs/verifier/judge.json 2>/logs/verifier/judge.err || true
fi

exit 0
