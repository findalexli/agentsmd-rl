#!/usr/bin/env bash
set -euo pipefail
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tail -50
echo "\"---REWARD---""
if python3 -m pytest test_outputs.py -q --tb=no 2>&1 | grep -q 'passed'; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
