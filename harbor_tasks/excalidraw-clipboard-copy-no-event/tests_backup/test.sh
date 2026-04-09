#!/bin/bash
set -e

# Install prettier globally for syntax checks
npm install -g prettier 2>/dev/null || true

# Install pytest
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run pytest
python3 -m pytest /tests/test_outputs.py -v
