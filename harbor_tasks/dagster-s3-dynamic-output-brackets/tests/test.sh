#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, writes binary reward

LOG_DIR="/logs/verifier"
REWARD_FILE="${LOG_DIR}/reward.txt"

mkdir -p "$LOG_DIR"

# Install pytest if not available
pip install pytest --quiet 2>/dev/null || true

# Run tests and capture results
cd /workspace/dagster || true

# Run pytest with verbose output and capture to file
python -m pytest /tests/test_outputs.py -v --tb=short > "${LOG_DIR}/pytest_output.txt" 2>&1 || true

# Simple parsing: count passed/failed
PASSED=$(grep -E "PASSED" "${LOG_DIR}/pytest_output.txt" 2>/dev/null | wc -l || echo "0")
FAILED=$(grep -E "FAILED" "${LOG_DIR}/pytest_output.txt" 2>/dev/null | wc -l || echo "0")
ERROR=$(grep -E "ERROR" "${LOG_DIR}/pytest_output.txt" 2>/dev/null | wc -l || echo "0")

# Trim whitespace
PASSED=$(echo "$PASSED" | tr -d ' ')
FAILED=$(echo "$FAILED" | tr -d ' ')
ERROR=$(echo "$ERROR" | tr -d ' ')

# Calculate reward: all tests must pass
TOTAL=$((PASSED + FAILED + ERROR))
if [ "$TOTAL" -eq 0 ]; then
    REWARD="0"
elif [ "$FAILED" -eq 0 ] && [ "$ERROR" -eq 0 ]; then
    REWARD="1"
else
    REWARD="0"
fi

# Write binary reward
echo "$REWARD" > "$REWARD_FILE"
# exit 0   # auto-disabled (prevented judge block from running)
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
