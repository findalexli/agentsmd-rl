#!/bin/bash
set -e

cd /workspace/kotlin

# Run pytest and capture output, but don't fail on test failures
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 || true

# Compute reward using Python (more reliable than bash parsing)
python3 << 'PYEOF'
import subprocess
import sys

result = subprocess.run(
    ["python3", "-m", "pytest", "/tests/test_outputs.py", "-q", "--tb=no"],
    capture_output=True,
    text=True
)

output = result.stdout + result.stderr

# Check for failures - if "failed" appears in output, reward is 0
if "failed" in output.lower():
    reward = "0"
else:
    # Check if all tests passed
    import re
    match = re.search(r'(\d+) passed', output)
    if match and int(match.group(1)) > 0:
        reward = "1"
    else:
        reward = "0"

with open("/logs/verifier/reward.txt", "w") as f:
    f.write(reward)

print(f"Reward: {reward}")
PYEOF
