#!/bin/bash
cd /workspace

# Run tests (pytest is already installed in the image)
# Don't use -e because pytest failure is expected for NOP test
python3 -m pytest /tests/test_outputs.py -v --tb=short
pytest_exit=$?

# Write binary reward based on pytest exit code
# pytest exit 0 = all tests passed = reward 1
# pytest exit 1 = some tests failed = reward 0
if [ $pytest_exit -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $pytest_exit
