#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest -q

# Create logs directory if it doesn't exist
mkdir -p /logs/verifier

# Run only the pass_to_pass tests
pytest /tests/test_outputs.py -v --tb=short -k "test_settings_importable or test_issue_module_importable or test_python_syntax_valid or test_no_broken_imports or test_repo_python_syntax_all_modified or test_repo_praktika_settings_import or test_repo_ci_settings_import or test_repo_praktika_modules_importable or test_repo_settings_attrs_accessible or test_repo_praktika_cli_works or test_repo_modified_files_ast_valid" 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
# If pytest succeeded (exit code 0), reward=1, else reward=0
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
