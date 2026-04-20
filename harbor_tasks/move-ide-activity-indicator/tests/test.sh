#!/usr/bin/env bash
set -e

# Install pytest if needed
python3 -m pip install pytest --break-system-packages 2>/dev/null || python3 -m pip install pytest || true

# Run the Python test file and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Get the exit code of pytest (using PIPESTATUS to get it from the pipe)
PYTEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward file based on pytest exit code
# pytest exits 0 when all tests pass, non-zero when any fail
if [ "$PYTEST_EXIT_CODE" -eq 0 ]; then
    echo "All tests passed"
    printf '\x01' > /logs/verifier/reward.bin
else
    echo "Some tests failed (exit code: $PYTEST_EXIT_CODE)"
    printf '\x00' > /logs/verifier/reward.bin
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
