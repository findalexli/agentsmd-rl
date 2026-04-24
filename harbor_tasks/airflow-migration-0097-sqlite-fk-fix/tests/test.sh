#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pytest-json-report -q

# Run tests with JSON output - ignore repo's pyproject.toml
cd /tests
python -m pytest test_outputs.py -v     -c /dev/null     --override-ini=addopts=     --json-report     --json-report-file=/logs/verifier/results.json     2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file based on test results
# Reward is 1 only if ALL tests pass (no failures)
if python -m pytest test_outputs.py --tb=no -q -c /dev/null --override-ini=addopts= 2>&1 | grep -qE "failed|error"; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
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
