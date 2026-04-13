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

## Copies and Modular Models

We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:

1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`. Ideally you should edit the code it's copying from and propagate the change, but you can break the `# Copied from` link if needed.
2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modeling` and other files from the `modular` file. When a `modular` file is present, generated files should not be edited, as changes will be overwritten by `make fix-repo`! Instead, edit the `modular` file. See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for a full guide on adding a model with `modular`, if needed, or you can inspect existing `modular` files as examples.
