#!/bin/bash
set -uo pipefail

TESTS_DIR="${TESTS_DIR:-/tests}"
LOG_DIR="${LOG_DIR:-/logs/verifier}"

pip install -q pytest 2>/dev/null || pip3 install -q pytest 2>/dev/null || true

mkdir -p "$LOG_DIR"

cd /workspace/kotlin

python3 -m pytest "$TESTS_DIR/test_outputs.py" -v --tb=short 2>&1 | tee "$LOG_DIR/test_output.log"
TEST_EXIT=${PIPESTATUS[0]}

if [ "$TEST_EXIT" -eq 0 ]; then
    echo "1" > "$LOG_DIR/reward.txt"
else
    echo "0" > "$LOG_DIR/reward.txt"
fi
