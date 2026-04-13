# Fix Division by Zero Bug

The `divide` function in `calculator.py` doesn't handle division by zero properly. When `b` is 0, it should raise a `ValueError` with the message "Cannot divide by zero" instead of letting Python raise a `ZeroDivisionError`.

## Task

Modify the `divide` function in `calculator.py` to:
1. Check if `b` is 0 before performing the division
2. Raise a `ValueError` with the exact message "Cannot divide by zero" when `b` is 0
3. Otherwise, return `a / b` as before

## Files to modify

- `calculator.py`: Fix the `divide` function

## Verification

The test `test_divide_by_zero` in `tests/test_calculator.py` should pass after your fix.
