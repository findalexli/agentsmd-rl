#!/usr/bin/env bash
# Minimal harness — runs pytest, writes binary reward from exit code.
set -uo pipefail

mkdir -p /logs/verifier

if ! python3 -c "import pytest" >/dev/null 2>&1; then
    /opt/pyenv/bin/pip install --quiet pytest==8.3.4
fi

export PATH="/opt/pyenv/bin:${PATH}"

cd /tests
python3 -m pytest -v --tb=short \
    -o cache_dir=/tmp/pytest-cache \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py
RC=$?

if [ "$RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
