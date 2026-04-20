#!/bin/bash
set -e

cd /tests

# Create virtual environment and install pytest
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install pytest --quiet

# Run the test file
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check result and write reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo '{"reward": 1, "message": "All tests passed"}' > /logs/verifier/reward.json
    exit 0
else
    echo "{\"reward\": 0, \"message\": \"Some tests failed\"}" > /logs/verifier/reward.json
    exit 1
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
