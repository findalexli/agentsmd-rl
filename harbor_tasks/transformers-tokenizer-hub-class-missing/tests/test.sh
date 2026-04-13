#!/usr/bin/env bash
set -uo pipefail
cd /tests
pip install pytest -q 2>/dev/null || true
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
exit $exit_code
