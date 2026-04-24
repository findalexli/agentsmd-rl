#!/bin/bash
set -e

cd /workspace/astro

# Build astro (needed for behavioral tests that run astro preview)
pnpm run build

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt

# Determine reward based on test results
python3 <<'PYEOF'
import re

with open('/logs/verifier/output.txt') as f:
    output = f.read()

# f2p tests (should fail on base commit, pass on fixed)
f2p_tests = [
    'test_user_vite_preview_allowedhosts_merged',
    'test_plugins_excluded_from_user_vite_config',
    'test_server_allowedhosts_precedence',
    'test_preview_uses_merged_config'
]

# p2p tests (should pass on base commit): lint, format, and eslint
p2p_tests = [
    'test_preview_lint',
    'test_preview_format',
    'test_preview_eslint'
]

# Parse pytest output properly - format is "testpath::test_name PASSED"
# or "testpath::test_name FAILED"
passed_tests = re.findall(r'::([^ ]+) PASSED', output)
failed_tests = re.findall(r'::([^ ]+) FAILED', output)

print(f"f2p_passed={[t for t in passed_tests if t in f2p_tests]}")
print(f"p2p_passed={[t for t in passed_tests if t in p2p_tests]}")
print(f"failed_tests={failed_tests}")

# For gold test (patch applied): all f2p tests should pass
# For NOP test (base commit): f2p tests should fail
all_f2p_passed = all(t in passed_tests for t in f2p_tests)

if all_f2p_passed:
    reward = 1
else:
    reward = 0

with open('/logs/verifier/reward.txt', 'w') as f:
    f.write(str(reward))

print(f"REWARD={reward}")
PYEOF
