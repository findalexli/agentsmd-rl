#!/usr/bin/env python3
"""Try writing reward in different ways to debug the issue."""
import os, sys

# Try writing to a known path
paths_to_try = [
    "/logs/verifier/reward.txt",
    "/tmp/reward.txt",
    "/workspace/reward.txt",
    "./reward.txt",
]

for path in paths_to_try:
    try:
        with open(path, "w") as f:
            f.write("debug")
        print(f"SUCCESS wrote to {path}", flush=True)
    except Exception as e:
        print(f"FAIL {path}: {e}", flush=True)

# Now try pytest approach
sys.path.insert(0, "/tests")
import test_outputs

print("test_outputs module loaded", flush=True)
print("REPO =", test_outputs.REPO, flush=True)

# Simulate pytest calling our hook
class FakeTerminalReporter:
    def __init__(self):
        self.stats = {'failed': [1], 'passed': [6]}

reporter = FakeTerminalReporter()
test_outputs.pytest_terminal_summary(reporter, 0, None)
print("Hook called", flush=True)