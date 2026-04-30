#!/usr/bin/env bash
set -euo pipefail

echo "=== Installing test dependencies ==="
pip install pytest==8.3.4 pyyaml==6.0.2 1>&2

echo "=== Running tests ==="
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 1>&2 && TEST_EXIT=0 || TEST_EXIT=$?

echo "=== Writing reward ==="
if [ $TEST_EXIT -eq 0 ]; then
	echo 1 > /logs/verifier/reward.txt
else
	echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (reserved for future judge integration)
