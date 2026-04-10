# Validation Task: transformers-processor-chat-template-kwargs

This is a benchmark validation task. The test suite in `tests/test_outputs.py`
verifies that the gold fix (PR #44881) correctly resolves the issue with
processor chat template kwargs.

## Validation Approach

1. NOP test: Run tests on base commit (before fix) - expect reward=0
   - Fail-to-pass tests should fail because the `_get_template_variables` function doesn't exist
   - Pass-to-pass tests should pass (existing functionality works)

2. Gold test: Apply solve.sh patch and run tests - expect reward=1
   - All tests should pass after the fix is applied

## Test Coverage

- Template variable extraction from Jinja2 templates
- Caching of extraction results
- Kwargs separation between template-level and processor-level
- Backward compatibility with existing functions
- Ruff style/format compliance
