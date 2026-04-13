#!/bin/bash
set -e

mkdir -p /logs/verifier

# Run the Python test file using pytest
python3 -c "
import sys
sys.path.insert(0, '/tests')
from test_outputs import *

# Run all test functions
tests = [name for name in dir() if name.startswith('test_')]
failed = []
for test_name in tests:
    try:
        globals()[test_name]()
        print(f'PASS: {test_name}')
    except Exception as e:
        print(f'FAIL: {test_name}: {e}')
        failed.append((test_name, str(e)))

# Write reward.txt
with open('/logs/verifier/reward.txt', 'w') as f:
    if failed:
        f.write('0')
        print(f'\n{len(failed)} test(s) failed:')
        for name, err in failed:
            print(f'  - {name}: {err}')
        sys.exit(1)
    else:
        f.write('1')
        print(f'\nAll {len(tests)} test(s) passed!')
        sys.exit(0)
"
