#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run the test suite
cd /workspace/task/tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file
# Parse the pytest output to determine pass/fail for each test
python3 << 'EOF'
import re
import json

# Read test output
with open("/logs/verifier/test_output.log", "r") as f:
    output = f.read()

# Parse results
results = {}
passed = 0
failed = 0

# Look for PASSED/FAILED patterns
for line in output.split("\n"):
    # Match patterns like "test_outputs.py::test_name PASSED"
    match = re.search(r"test_outputs\.py::(\w+)\s+(PASSED|FAILED|ERROR)", line)
    if match:
        test_name = match.group(1)
        status = match.group(2)
        results[test_name] = 1.0 if status == "PASSED" else 0.0
        if status == "PASSED":
            passed += 1
        else:
            failed += 1

# Calculate total score
total_tests = len(results)
total_score = sum(results.values()) if total_tests > 0 else 0.0

# Write reward manifest
reward = {
    "total_score": total_score,
    "max_score": float(total_tests),
    "results": results
}

with open("/logs/verifier/reward.json", "w") as f:
    json.dump(reward, f, indent=2)

print(f"\n{'='*60}")
print(f"Tests passed: {passed}/{total_tests}")
print(f"Total score: {total_score}/{total_tests}")
print(f"{'='*60}")

# Exit with error if any tests failed
if failed > 0:
    exit(1)
EOF
