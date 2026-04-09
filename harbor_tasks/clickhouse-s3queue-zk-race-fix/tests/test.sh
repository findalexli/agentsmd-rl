#!/bin/bash
set -e

echo "Installing pytest if needed..."
pip3 install pytest pyyaml -q

echo "Running tests..."
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract final result
if grep -q "passed" /logs/verifier/test_output.log && ! grep -q "failed" /logs/verifier/test_output.log; then
    echo "All tests passed"
    echo '{"passed": true, "score": 1.0, "max_score": 1.0}' > /logs/verifier/result.json
    exit 0
else
    echo "Some tests failed"
    # Count passes and fails
    PASSED=$(grep -oP '\d+(?= passed)' /logs/verifier/test_output.log | tail -1 || echo "0")
    FAILED=$(grep -oP '\d+(?= failed)' /logs/verifier/test_output.log | tail -1 || echo "0")
    TOTAL=$((PASSED + FAILED))
    if [ "$TOTAL" -eq 0 ]; then
        SCORE=0
    else
        SCORE=$(python3 -c "print($PASSED / $TOTAL)")
    fi
    echo "{\"passed\": false, \"score\": $SCORE, \"max_score\": 1.0, \"passed_tests\": $PASSED, \"total_tests\": $TOTAL}" > /logs/verifier/result.json
    exit 1
fi
