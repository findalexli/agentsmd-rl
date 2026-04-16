# Add Documentation to `default_user_agent`

The function `default_user_agent(name="python-requests")` in `src/requests/utils.py` returns a user agent string in the format `"{name}/{version}"`.

## Requirements

1. **Parameter documentation**: The docstring must document the `name` parameter using the `:param name:` field.

2. **Description or example**: The docstring must include either:
   - An `Example:` section showing usage (e.g., `Example: 'python-requests/2.31.0'`), OR
   - A phrase like `library name and version` that describes what the function returns

3. **Preserve existing behavior**: The function signature `def default_user_agent(name="python-requests"):` and return value format must remain unchanged.

## Verification

After editing, ensure:
- `ruff check src/requests/utils.py` passes
- `ruff format --check src/requests/utils.py` passes
- `pytest tests/test_utils.py` passes
- `python -c "from requests.utils import default_user_agent; ua = default_user_agent(); assert 'python-requests' in ua"` succeeds
