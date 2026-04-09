#!/bin/bash
set -e

# Install pytest, ruff (pinned to repo version), and sphinx/docutils
pip install pytest "ruff==0.15.0" sphinx docutils -q

# Run the tests
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $EXIT_CODE
