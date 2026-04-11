#!/bin/bash
set -e

cd /tests
pip install ruff -q 2>/dev/null || true

echo "Running pass-to-pass tests..."
python3 -c "
import test_outputs
test_outputs.test_file_exists()
print('test_file_exists: PASS')
test_outputs.test_kernel_function_present()
print('test_kernel_function_present: PASS')
test_outputs.test_kernel_header_valid()
print('test_kernel_header_valid: PASS')
test_outputs.test_repo_python_syntax()
print('test_repo_python_syntax: PASS')
test_outputs.test_repo_ruff_check()
print('test_repo_ruff_check: PASS')
test_outputs.test_repo_import_sglang_jit_kernel()
print('test_repo_import_sglang_jit_kernel: PASS')
test_outputs.test_repo_git_tracks_file()
print('test_repo_git_tracks_file: PASS')
"

echo ""
echo "All pass-to-pass tests passed!"
