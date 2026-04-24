# Fix: Stop propagating config items to metadata

## Problem

The `ensure_config()` function in `libs/langgraph/langgraph/_internal/_config.py` is incorrectly propagating items from the `configurable` dict into the `metadata` dict. This is causing unexpected keys to appear in metadata that should only contain explicitly provided metadata.

## Current Behavior (Broken)

When you call `ensure_config()` with a config like:

```python
config = {
    "configurable": {
        "includeme": "hi",
        "andme": 42,
        "api_key": "secret",
    },
    "metadata": {"existing": "value"},
}
```

The resulting metadata incorrectly contains config items:
```python
merged["metadata"].keys()  # => {"includeme", "andme", "existing"}
```

## Expected Behavior (Fixed)

Config items should stay in `configurable`, NOT be propagated to `metadata`:
```python
merged["metadata"].keys()  # => {"existing"}  # only original metadata
merged["configurable"]["includeme"]  # => "hi"  # still in configurable
```

## Files to Modify

1. `libs/langgraph/langgraph/_internal/_config.py` - Fix the `ensure_config()` function
2. `libs/langgraph/tests/test_utils.py` - Update the test expectation (the test `test_configurable_metadata`)

## Testing

After your fix, the test `test_configurable_metadata` in `test_utils.py` should pass.

The test currently expects metadata to contain `{"includeme", "andme", "nooverride"}`, but after your fix it should only contain `{"nooverride"}`.

## Notes

- You may need to remove some helper code that was used for the filtering/propagation logic
- The fix should NOT change where config items are stored - they should remain in `configurable`
- Run the repo's test suite after making changes: `make test` in `libs/langgraph/`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `mypy (Python type checker)`
