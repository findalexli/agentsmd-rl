# Fix Division by Zero Bug

The `divide` function in `src/calc.py` currently does not handle division by zero. When `b` is 0, it should raise a `ValueError` with the message "Cannot divide by zero".

## Requirements

1. Modify `src/calc.py` to handle division by zero in the `divide` function
2. Update `.claude/CLAUDE.md` with the error handling convention

## Files to Modify

- `src/calc.py` - Add validation for `b == 0`
- `.claude/CLAUDE.md` - Document the error handling convention

## Example

```python
>>> from calc import divide
>>> divide(10, 0)
ValueError: Cannot divide by zero
```
