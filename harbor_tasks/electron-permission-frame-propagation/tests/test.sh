#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest pyyaml -q

# Run tests and capture results
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Check if all pass_to_pass tests passed
# We look for lines like "PASSED" for pass_to_pass tests and "FAILED" for fail_to_pass tests
# If any pass_to_pass test failed, reward is 0, otherwise 1

# Count pass_to_pass tests that passed vs failed
p2p_passed=$(grep -c "PASSED" /logs/verifier/test_output.log || echo "0")
p2p_failed=$(grep "FAILED" /logs/verifier/test_output.log | grep -v "test_check_\|test_web_contents\|test_serial\|test_no_web" | wc -l || echo "0")

# The pass_to_pass tests are:
# - test_header_guards_follow_convention
# - test_clang_format
# - test_modified_headers_have_guards
# - test_cpplint
# - test_modified_files_exist
# - test_serial_delegate_has_can_request_port_permission
# - test_web_contents_permission_helper_structure
# - test_shell_directory_clang_format
# - test_git_repository_valid
# - test_no_merge_conflict_markers
# - test_file_utf8_encoding
# - test_no_trailing_whitespace_in_modified

# Check specifically for pass_to_pass test failures
p2p_failures=$(grep "FAILED" /logs/verifier/test_output.log | grep -E "(header_guards_follow_convention|clang_format|modified_headers_have_guards|cpplint|modified_files_exist|serial_delegate_has|web_contents_permission_helper_structure|shell_directory_clang_format|git_repository_valid|no_merge_conflict_markers|file_utf8_encoding|no_trailing_whitespace)" | wc -l || echo "0")

if [ "$p2p_failures" -eq "0" ]; then
    echo "1" > /logs/verifier/reward
    echo "All pass_to_pass tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some pass_to_pass tests failed."
fi

exit 0
