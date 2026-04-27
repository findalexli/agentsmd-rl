#!/bin/bash
# Standard pytest-driven test runner. Reward is pytest's exit code, written
# as literal "0" or "1" to /logs/verifier/reward.txt.

set -u

mkdir -p /logs/verifier

# Run pytest with CTRF JSON for downstream inspection.
pytest /tests/test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json
PYTEST_RC=$?

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# The harness may attach a standalone judge that reads /logs/verifier/ctrf.json
# and the rubric. This block is intentionally empty here; do not add an early
# exit above it.
if [ -f /tests/standalone_judge.py ]; then
    python3 /tests/standalone_judge.py || true
fi

exit 0
