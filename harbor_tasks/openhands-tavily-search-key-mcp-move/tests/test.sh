#!/usr/bin/env bash
# Standardised harness test runner. Reward MUST be the literal string "0" or
# "1" written to /logs/verifier/reward.txt; the value is taken directly from
# pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/openhands

# pytest + ctrf reporter are already baked into the image in /opt/pytest-venv.
PYTEST_BIN="/opt/pytest-venv/bin/pytest"
if [ ! -x "$PYTEST_BIN" ]; then
    echo "FATAL: pytest binary missing from image at $PYTEST_BIN" >&2
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

"$PYTEST_BIN" /tests/test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json
exit_code=$?

if [ "$exit_code" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
