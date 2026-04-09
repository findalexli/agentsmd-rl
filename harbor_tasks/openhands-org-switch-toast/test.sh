#!/bin/bash
set -e

echo "=== Setting up test environment ==="
cd /workspace/task/tests

# Install pytest if not already installed
pip install pytest --quiet

echo "=== Running tests ==="
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "=== All tests passed ==="
    echo "1.0" > /logs/verifier/reward.txt
    exit 0
else
    echo "=== Some tests failed ==="
    # Count how many tests passed vs failed
    PASSED=$(grep -c "PASSED" /logs/verifier/test_output.log || echo "0")
    FAILED=$(grep -c "FAILED" /logs/verifier/test_output.log || echo "0")
    TOTAL=$((PASSED + FAILED))

    if [ "$TOTAL" -gt 0 ]; then
        REWARD=$(echo "scale=2; $PASSED / $TOTAL" | bc)
        echo "$REWARD" > /logs/verifier/reward.txt
    else
        echo "0.0" > /logs/verifier/reward.txt
    fi
    exit 0  # Exit 0 so the harness doesn't think we crashed
fi
