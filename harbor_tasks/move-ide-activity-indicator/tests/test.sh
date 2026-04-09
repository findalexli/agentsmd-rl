#!/usr/bin/env bash
set -e

# Install pytest if needed
python3 -m pip install pytest --break-system-packages 2>/dev/null || python3 -m pip install pytest || true

# Run the Python test file
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file based on test results
# Count passed tests
total_tests=$(grep -c "def test_" test_outputs.py || echo "0")
passed_tests=$(grep -c "PASSED" /logs/verifier/test_output.log || echo "0")

if [ "$passed_tests" -eq "$total_tests" ] && [ "$total_tests" -gt 0 ]; then
    echo "All tests passed"
    printf '\x01' > /logs/verifier/reward.bin
else
    echo "Some tests failed: $passed_tests / $total_tests passed"
    printf '\x00' > /logs/verifier/reward.bin
fi
