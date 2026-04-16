#!/usr/bin/env bash
# Don't use set -e because we need to capture pytest exit code

# Install deno if not available (needed for behavioral tests)
if ! command -v deno &>/dev/null; then
    apt-get update -qq && apt-get install -y -qq unzip curl >/dev/null 2>&1 || true
    curl -fsSL https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip -o /tmp/deno.zip 2>/dev/null || true
    unzip -o /tmp/deno.zip -d /usr/local/bin/ >/dev/null 2>&1 || true
    chmod +x /usr/local/bin/deno 2>/dev/null || true
fi

# Ensure python3 + pip + pytest are available
if ! python3 -c "import pytest" 2>/dev/null; then
    if ! command -v pip3 &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq python3-pip python3-venv >/dev/null 2>&1 || true
    fi
    python3 -m pip install -q pytest pytest-json-ctrf 2>/dev/null || \
        pip3 install -q --break-system-packages pytest pytest-json-ctrf 2>/dev/null || true
fi

# Run pytest and capture exit code
python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA --tb=short -q
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
