#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest || true

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Calculate reward (number of tests passed / total tests)
REWARD=$(python3 -c "
import re
with open('/logs/verifier/pytest.log', 'r') as f:
    content = f.read()

# Find passed/total pattern
match = re.search(r'(\\d+) passed', content)
total_match = re.search(r'passed.*?in', content)

if match:
    passed = int(match.group(1))
    # Get total tests from the collection message
    total_match = re.search(r'collected (\\d+) items', content)
    if total_match:
        total = int(total_match.group(1))
        reward = passed / total
        print(f'{reward:.4f}')
    else:
        print('0.0000')
else:
    print('0.0000')
")

# Write binary reward (1 if all passed, 0 otherwise)
if echo "$REWARD" | grep -q "1.0000\|0.9999"; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
