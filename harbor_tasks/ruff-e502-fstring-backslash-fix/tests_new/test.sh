#!/usr/bin/env bash
set -euo pipefail

# Install pytest if not available
if ! python3 -c "import pytest" 2>/dev/null; then
    apt-get update -qq && apt-get install -y -qq python3-pytest 2>/dev/null
fi

cd /tests
python3 -m pytest test_outputs.py -v "$@"
