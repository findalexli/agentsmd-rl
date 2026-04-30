#!/usr/bin/env bash
# Standardized harbor test runner. Reward (`0` or `1` literal) is written to
# /logs/verifier/reward.txt directly from pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

# Make the custom vitest test file available inside the repo so workspace path
# aliases (@excalidraw/*) resolve correctly.
mkdir -p /workspace/excalidraw/packages/element/tests
cp /tests/oob_fix.test.tsx /workspace/excalidraw/packages/element/tests/__oob_fix__.test.tsx

cd /workspace
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"
