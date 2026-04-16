#!/bin/bash
set -e

# Setup Python virtual environment for installing packages
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate

# Install pytest and run tests
/tmp/venv/bin/pip install pytest --quiet
/tmp/venv/bin/python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward (1 if all tests passed, 0 otherwise)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
