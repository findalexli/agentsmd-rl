#!/bin/bash
set -euo pipefail

# Install pytest if not present
if ! command -v pytest &>/dev/null; then
    pip3 install --break-system-packages pytest==8.3.4 2>/dev/null || pip install pytest==8.3.4 2>/dev/null || true
fi

# Run tests
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="/workspace/civitai"

cd "$REPO_DIR"

TEST_RESULT=0
python3 -m pytest "$TEST_DIR/test_outputs.py" -v --tb=short 2>&1 || TEST_RESULT=$?

# Write reward
if [ $TEST_RESULT -eq 0 ]; then
    echo -n "1" > /logs/verifier/reward.txt
else
    echo -n "0" > /logs/verifier/reward.txt
    # exit 1   # auto-disabled (prevented judge block from running)
fi

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
