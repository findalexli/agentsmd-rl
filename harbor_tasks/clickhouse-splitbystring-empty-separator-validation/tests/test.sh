#!/bin/bash
set -e

# Standardized test runner - DO NOT MODIFY

pip3 install pytest pyyaml -q 2>/dev/null || pip install pytest pyyaml -q 2>/dev/null

cd /workspace/ClickHouse

pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward
if grep -q "passed" /logs/verifier/pytest.log && ! grep -q "failed" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Test completed. Reward: $(cat /logs/verifier/reward.txt)"
