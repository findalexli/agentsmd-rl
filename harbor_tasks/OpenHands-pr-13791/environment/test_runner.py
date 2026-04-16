#!/usr/bin/env python3
"""Minimal test runner that executes the repo's own tests."""

import subprocess
import sys
import os

os.chdir('/workspace/openhands')

# Run the repo's own unit tests
result = subprocess.run(
    [
        'python', '-m', 'pytest',
        'enterprise/tests/unit/test_slack_integration.py',
        '-v', '--tb=short',
        '-x',
    ],
    capture_output=True,
    text=True,
    timeout=120,
)

print(result.stdout)
if result.stderr:
    print(result.stderr)

sys.exit(result.returncode)
