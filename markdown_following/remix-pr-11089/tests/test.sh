#!/usr/bin/env bash
set -uo pipefail

# Bootstrap pytest if not already available (e.g. on non-Python base images)
if ! python3 -c "import pytest" 2>/dev/null; then
    pip install pytest==8.3.4
fi

python3 -m pytest /tests/test_outputs.py -v --tb=short
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
