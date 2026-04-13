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
    echo "1" > /logs/verifier/reward
    echo "All pass_to_pass tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some pass_to_pass tests failed."
fi

exit 0
