# Fix Division by Zero Bug

The `divide` function in `calculator.py` currently raises a `ZeroDivisionError` when the second argument is 0. This behavior is incorrect.

## Task

Modify the `divide` function in `calculator.py` such that:
- Calling `divide(a, 0)` for any value of `a` raises `ValueError` with the exact message `"Cannot divide by zero"`
- Calling `divide(a, b)` where `b` is non-zero continues to return the correct quotient

## Files to modify

- `calculator.py`: Fix the `divide` function

## Verification

The test `test_divide_by_zero` in `tests/test_calculator.py` should pass after your fix.
