# Fix sum_numbers empty list handling

The `sum_numbers` function in `mymath.py` currently returns `None` when given an empty list. This is incorrect behavior - it should return `0` since the sum of an empty list of numbers is mathematically 0.

## Task

Fix the `sum_numbers` function to return `0` instead of `None` when given an empty list.

## Expected behavior

- `sum_numbers([])` should return `0` (currently returns `None`)
- `sum_numbers([1, 2, 3])` should return `6`
- `sum_numbers([10])` should return `10`

## Files to modify

- `mymath.py` - Fix the empty list check to return 0 instead of None
