#!/bin/bash
set -e

# Install pytest if not present
pip install pytest pyyaml -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run tests
cd /workspace/langchain/libs/core
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Determine reward based on test results
# The critical tests are:
# 1. test_symlink_bypass_blocked (f2p)
# 2. test_symlink_yaml_to_py_blocked (f2p)
# 3. test_symlink_yml_to_py_blocked (f2p)
# These must all pass for the fix to be considered working

REWARD=0
if grep -q "test_symlink_bypass_blocked PASSED" /logs/verifier/test_output.txt && \
   grep -q "test_symlink_yaml_to_py_blocked PASSED" /logs/verifier/test_output.txt && \
   grep -q "test_symlink_yml_to_py_blocked PASSED" /logs/verifier/test_output.txt; then
    REWARD=1
fi

echo "$REWARD" > /logs/verifier/reward.txt
echo "Reward: $REWARD"
exit 0

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
