#!/bin/bash
set -e

echo "==> Installing pytest..."
pip3 install pytest --quiet

echo "==> Running tests..."
cd /tests

# Run tests and capture exit code (PIPESTATUS doesn't work with set -e)
set +e
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
exit_code=${PIPESTATUS[0]}
set -e

# Write binary reward file
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "==> All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "==> Some tests failed"
fi

exit $exit_code
