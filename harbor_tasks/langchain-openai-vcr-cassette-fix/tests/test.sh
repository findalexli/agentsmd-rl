#!/bin/bash
set -e

# Install pytest and pytest-recording if not already installed
pip install pytest pytest-recording --quiet

# Run tests with verbose output
cd /workspace/langchain/libs/partners/openai

# Set fake API key for VCR playback mode
export OPENAI_API_KEY="sk-fake"

# Run the test file mounted from /tests
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
