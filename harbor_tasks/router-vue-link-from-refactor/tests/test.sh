#!/bin/bash
set -e

# Install pytest if needed
pip install pytest --quiet

# Run tests and write reward
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
