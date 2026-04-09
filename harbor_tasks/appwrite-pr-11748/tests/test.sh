#!/bin/bash
set -e

cd /tests

# Create virtual environment and install pytest
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install pytest --quiet

# Run the test file
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check result and write reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo '{"reward": 1, "message": "All tests passed"}' > /logs/verifier/reward.json
    exit 0
else
    echo "{\"reward\": 0, \"message\": \"Some tests failed\"}" > /logs/verifier/reward.json
    exit 1
fi
