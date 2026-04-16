#!/bin/bash

cd /workspace/payload_repo

# Install pytest if needed
pip3 install pytest --break-system-packages -q 2>/dev/null || true

# Run pytest on test_outputs.py
python3 -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?

# Write reward
if [ $PYTEST_EXIT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT
