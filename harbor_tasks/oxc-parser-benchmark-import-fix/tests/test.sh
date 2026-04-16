#!/bin/bash
set -e

# Install pytest if needed
if ! command -v pytest &> /dev/null; then
    pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest
fi

# Install node dependencies for napi/parser (needed for vitest tests)
cd /workspace/oxc/napi/parser
pnpm install --prefer-offline 2>/dev/null || pnpm install

# Run the tests
cd /workspace/oxc
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check if all tests passed
if grep -q "PASSED" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
