#!/bin/bash
set -e

# Install pytest
pip install pytest -q

# Run tests
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
