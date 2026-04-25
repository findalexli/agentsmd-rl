# Revert invocation params metadata tracing

## Problem

The `langchain-core` package currently traces invocation parameters in run metadata. This includes model parameters like `model`, `temperature`, etc. in the metadata of traced runs. This logic needs to be reverted - invocation params should NOT be automatically included in metadata.

## Files to modify

1. `libs/core/langchain_core/language_models/chat_models.py` - Remove the `_get_metadata_invocation_params` method and its usages in:
   - `stream()`
   - `astream()`
   - `generate()`
   - `agenerate()`

2. `libs/core/tests/unit_tests/language_models/chat_models/test_base.py` - Remove:
   - `FakeChatModelWithSecrets` test class
   - All tests related to invocation params in metadata (tests starting with `test_init_params_*`, `test_runtime_*`, `test_invocation_params_*`, `test_user_metadata_*`)

## Expected behavior after fix

- The `_get_metadata_invocation_params` method should not exist
- The `inheritable_metadata` dict in stream/astream/generate/agenerate should only include user-provided metadata and ls_params, NOT invocation params
- Model parameters should NOT automatically appear in run metadata

## What NOT to do

- Do NOT add new tests (this is a revert, tests are being removed)
- Do NOT change any other functionality
- Do NOT modify public function signatures (this is a revert, not a refactor)

## Testing

Run unit tests to verify:
```bash
cd libs/core
python -m pytest tests/unit_tests/language_models/chat_models/test_base.py -v
```

All existing tests should continue to pass after removing the feature-specific tests.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `mypy (Python type checker)`
