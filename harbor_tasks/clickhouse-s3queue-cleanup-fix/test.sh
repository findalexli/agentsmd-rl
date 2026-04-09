#!/bin/bash
set -e

pip3 install pytest pyyaml -q

cd /workspace/tests

python3 -m pytest test_outputs.py -v 2>&1 | tee /workspace/test_output.log

# Write binary reward
if grep -q "PASSED" /workspace/test_output.log && ! grep -q "FAILED" /workspace/test_output.log; then
    echo "1" > /workspace/reward.txt
else
    echo "0" > /workspace/reward.txt
fi

echo "Tests complete. Reward: $(cat /workspace/reward.txt)"
