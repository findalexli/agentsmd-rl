#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest pyyaml -q

# Run tests and capture results
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check specifically for pass_to_pass test failures
p2p_failures=$(grep "FAILED" /logs/verifier/test_output.log | grep -E "(header_guards_follow_convention|clang_format|modified_headers_have_guards|cpplint|modified_files_exist|serial_delegate_has|web_contents_permission_helper_structure|shell_directory_clang_format|git_repository_valid|no_merge_conflict_markers|file_utf8_encoding|no_trailing_whitespace|patches_config_valid|patches_directory_structure|clang_format_shell_browser|cpplint_modified_files|shell_common_clang_format|git_no_uncommitted_changes)" | wc -l || echo "0")

if [ "$p2p_failures" -eq "0" ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All pass_to_pass tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some pass_to_pass tests failed."
fi

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
