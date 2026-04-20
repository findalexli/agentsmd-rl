#!/bin/bash
set -e

REPO_DIR="/workspace/ant-design"
LOGS_DIR="/logs/verifier"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Install pytest if not available
pip3 install pytest --quiet 2>/dev/null || pip install pytest --quiet 2>/dev/null || true

# Run the test file directly to get the REWARD output
python3 /tests/test_outputs.py 2>&1 | tee "$LOGS_DIR/test_output.log"

# Extract the binary reward from the test output
# The test should output a line like "REWARD: 1" or "REWARD: 0"
if grep -q "REWARD:" "$LOGS_DIR/test_output.log"; then
    REWARD=$(grep "REWARD:" "$LOGS_DIR/test_output.log" | tail -1 | sed 's/.*REWARD: \([0-9.]*\).*/\1/')
    echo ""
    echo "========================================"
    echo "FINAL REWARD: $REWARD"
    echo "========================================"
    # Write reward to a file for the harness
    echo "$REWARD" > "$LOGS_DIR/reward.txt"
else
    echo "No REWARD line found in test output"
    echo "0" > "$LOGS_DIR/reward.txt"
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
