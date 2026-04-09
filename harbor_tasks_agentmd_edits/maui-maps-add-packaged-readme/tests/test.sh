#!/usr/bin/env bash
set -e

echo "=== Running test_outputs.py ==="
python3 -m pytest /workspace/task/tests/test_outputs.py -v --tb=short 2>&1
