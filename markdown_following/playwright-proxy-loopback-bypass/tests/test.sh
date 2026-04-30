#!/bin/bash
set -e

REPO=/workspace/playwright
LOGS=/logs/verifier
mkdir -p "$LOGS"

# Install ts-node for behavioral TypeScript tests
cd /workspace/playwright
npm install -g ts-node typescript 2>&1 | tail -5 || true

# Run pytest with proper Python path
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOGS/pytest_output.txt"

# Determine reward based on test results
if grep -q "passed" "$LOGS/pytest_output.txt" && ! grep -q "FAILED" "$LOGS/pytest_output.txt"; then
    echo "1" > "$LOGS/reward.txt"
else
    echo "0" > "$LOGS/reward.txt"
fi

cat "$LOGS/reward.txt"

# --- LLM Judge (Track 3 + Track 4) ---
if [ -f /tests/eval_manifest.yaml ] && [ -f /tests/standalone_judge.py ]; then
    # Capture agent diff
    mkdir -p /logs/verifier
    _repo_dir=""
    for candidate in /workspace/*/ /repo /app /src; do
        if [ -d "${candidate}/.git" ]; then
            _repo_dir="$candidate"
            break
        fi
    done
    if [ -z "$_repo_dir" ]; then
        _repo_dir=$(find /workspace /repo /app /src -maxdepth 3 -type d -name .git 2>/dev/null | head -1 | xargs -r dirname)
    fi
    if [ -n "$_repo_dir" ] && [ -d "$_repo_dir/.git" ]; then
        (cd "$_repo_dir" && git add -A 2>/dev/null && git diff --cached > /logs/verifier/agent.diff 2>/dev/null) || true
    fi

    # Install PyYAML if needed (lightweight, <1s)
    python3 -c "import yaml" 2>/dev/null || \
        python3 -m pip install -q pyyaml 2>/dev/null || \
        pip3 install -q --break-system-packages pyyaml 2>/dev/null || true

    # Run LLM judge (writes track3_rubric.json + track4_distractors.json)
    python3 /tests/standalone_judge.py /tests/eval_manifest.yaml /logs/verifier/agent.diff 2>&1 || true
fi
