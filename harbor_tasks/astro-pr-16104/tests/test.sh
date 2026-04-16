#!/bin/bash
set -e

cd /workspace/astro

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt

# Determine reward based on test results
python3 <<'PYEOF'
import re

with open('/logs/verifier/output.txt') as f:
    output = f.read()

# f2p tests (should fail on base commit): the ones checking for mergeConfig
f2p_tests = [
    'test_preview_uses_mergeConfig',
    'test_vite_preview_allowed_hosts_merged_in_config',
    'test_allowedHosts_precedence_logic'
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

f2p_passed_list = [t for t in passed_tests if t in f2p_tests]
p2p_passed_list = [t for t in passed_tests if t in p2p_tests]

print(f"f2p_passed={f2p_passed_list}")
print(f"p2p_passed={p2p_passed_list}")
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