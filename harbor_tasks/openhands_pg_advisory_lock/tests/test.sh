#!/bin/bash
set -e

export REPO=/workspace/gradio
export GRADIO_ANALYTICS_ENABLED=False
export HF_HUB_DISABLE_TELEMETRY=True

cd /tests

# Run all tests using pytest
python -m pytest test_outputs.py -v --tb=short 2>&1

# Capture exit code
TEST_EXIT=${PIPESTATUS[0]}

# Write reward
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $TEST_EXIT
