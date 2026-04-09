#!/bin/bash
set -e

cd /workspace

# Install pytest if not already installed
# pytest already installed via apt

# Run the tests and capture output (allow failure with || true)
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Count total tests from collect-only (suppress stderr)
TOTAL=$(python3 -m pytest /tests/test_outputs.py --collect-only -q 2>/dev/null | grep -oP '\d+(?= tests collected)' || echo "1")

# Count passed tests from test run summary (suppress stderr)
# Parse the summary line like "3 failed, 4 passed, 3 warnings in 48.76s"
PASSED=$(python3 -m pytest /tests/test_outputs.py -q 2>/dev/null | grep -oP '\d+(?= passed)' || echo "0")

if [ -z "$PASSED" ]; then PASSED=0; fi
if [ -z "$TOTAL" ] || [ "$TOTAL" -eq 0 ]; then TOTAL=1; fi

# Calculate reward as fraction of passed tests
REWARD=$(python3 -c "print($PASSED / $TOTAL)")
echo "REWARD: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Exit with success if all tests passed
if [ "$PASSED" -eq "$TOTAL" ]; then
    exit 0
else
    exit 1
fi
