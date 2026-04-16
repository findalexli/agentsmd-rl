# Fix structlog dict argument formatting

## Problem

When logging a dictionary as a positional argument with a `%s` format specifier, the structlog integration throws a `TypeError`. For example:

```python
logger.warning("Info message %s", {"a": 10})
```

This should output `Info message {'a': 10}`, but instead raises:
```
TypeError: format requires a mapping
```

## Expected behavior

The fix must satisfy these behaviors:

1. `log.info("data: %s", {"key": "value"})` should produce `data: {'key': 'value'}`
2. `log.warning("%(name)s says hi", {"name": "Alice"})` should produce `Alice says hi`
3. Multiple different dict contents should work with `%s` formatting
4. A formatter function must be added to the `airflow_shared.logging.structlog` module that:
   - Is importable from `airflow_shared.logging.structlog`
   - Accepts a `(logger, method_name, event_dict)` signature where `event_dict` is a dict with `event` and `positional_args` keys
   - Consumes the `positional_args` key from `event_dict` (removes it after processing)
   - Preserves all other keys in `event_dict`
   - Handles `TypeError` and `KeyError` exceptions when formatting log arguments with dict values
5. The source code must handle both `TypeError` and `KeyError` exceptions when formatting log arguments

## CPython stdlib reference

The structlog integration should follow the same dict-argument formatting behavior as Python's stdlib `logging` module. The stdlib logging tries positional formatting first (e.g., `"%s" % {"a": 1}`) and only falls back to named substitution if that raises `TypeError` or `KeyError`.
