#!/bin/bash
set -euo pipefail

# Standard test runner for benchmark tasks
# Installs pytest if needed and runs test_outputs.py

echo "=== Installing pytest ==="
pip install pytest --quiet

echo "=== Running tests ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
exit_code=0
python -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log || exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "=== All tests passed ==="
else
    echo "0" > /logs/verifier/reward.txt
    echo "=== Some tests failed ==="
fi

exit $exit_code
