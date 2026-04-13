# Fix CaseInsensitiveDict pop() to return default value

## Problem

The `CaseInsensitiveDict` class in `requests/structures.py` has a bug where the `pop()` method doesn't return the default value when the key is not found. Instead, it raises a `KeyError`.

## Task

1. Fix the `pop()` method in `CaseInsensitiveDict` to correctly return the default value when the key is not found
2. The fix should maintain backward compatibility and follow existing code style

## Files to modify

- `src/requests/structures.py` - Fix the `pop()` method in `CaseInsensitiveDict`

## Testing

After fixing, the following should work:

```python
from requests.structures import CaseInsensitiveDict

d = CaseInsensitiveDict()
d['Key'] = 'value'

# Should return 'default' instead of raising KeyError
result = d.pop('nonexistent', 'default')
assert result == 'default'
```

Run the tests in `tests/test_structures.py` to verify your fix works correctly.
