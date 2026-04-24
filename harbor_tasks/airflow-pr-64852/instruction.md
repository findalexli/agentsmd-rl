# Theme Configuration Issue

The Airflow UI theme configuration system currently requires the `tokens` field to be provided, but users want more flexibility. Specifically, they should be able to:

1. Provide only CSS overrides via `globalCss` without any color tokens
2. Provide only a custom icon without other theme customization
3. Provide an empty configuration `{}` to restore OSS defaults

Currently, attempting to create a theme without the `tokens` field fails with a validation error.

## Files of Interest

- `airflow-core/src/airflow/api_fastapi/common/types.py` - Contains the `Theme` and `ThemeColors` Pydantic models
- `airflow-core/src/airflow/api_fastapi/core_api/datamodels/ui/config.py` - Contains the `ConfigResponse` model that serializes theme configuration

## Expected Behavior

Users should be able to configure themes in multiple ways:

```python
# CSS-only theme (no tokens)
Theme(globalCss={"body": {"background": "white"}})

# Icon-only theme
Theme(icon="custom-logo.svg")

# Empty theme to restore defaults
Theme()

# Full theme with tokens (should still work)
Theme(tokens={"colors": colors}, globalCss={"body": {...}})
```

The API response should also properly serialize themes that have optional fields, excluding `None` values from the JSON output.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
