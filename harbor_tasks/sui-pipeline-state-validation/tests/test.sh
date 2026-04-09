#!/bin/bash
set -euo pipefail

echo "=== Installing pytest ==="
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

echo "=== Running tests ==="
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

exit_code=${PIPESTATUS[0]}

echo "=== Writing binary reward ==="
if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward
else
    echo 0 > /logs/verifier/reward
fi

echo "Exit code: $exit_code"
exit $exit_code
