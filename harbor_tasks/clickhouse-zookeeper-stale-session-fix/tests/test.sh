#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run tests
cd /workspace/clickhouse
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward
REWARD_FILE=/logs/verifier/reward.txt
PASSED=$(grep -c "PASSED" /logs/verifier/pytest_output.txt || true)
TOTAL=$(grep -c "test_.*::" /logs/verifier/pytest_output.txt || true)

if [ "$PASSED" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "1" > "$REWARD_FILE"
    echo "All tests passed"
else
    echo "0" > "$REWARD_FILE"
    echo "Some tests failed: $PASSED/$TOTAL"
fi
