# Fix formatDateTime %W Variable-Width Formatter Bug

## Problem

The `formatDateTime` function has a bug where the `%W` formatter (weekday name) is not consistently treated as a variable-length formatter. The weekday name varies in length (e.g., "Monday" = 6 chars, "Wednesday" = 9 chars), so it should always be considered variable-width regardless of settings.

Currently, the code in `src/Functions/formatDateTime.cpp` has logic that only treats `%W` as variable-width in certain code paths, specifically when the `mysql_M_is_month_name` setting is false. This causes incorrect behavior when that setting is true.

## What You Need to Do

Modify the `containsOnlyFixedWidthMySQLFormatters` function in `src/Functions/formatDateTime.cpp` to:

1. **Remove `%W` from the `variable_width_formatter_M_is_month_name` array** - this array should only contain `'M'` after the fix

2. **Move the `%W` check to be unconditional** - the check for `%W` should happen BEFORE the `mysql_M_is_month_name` conditional, so it always returns false (indicating variable-width) regardless of that setting

3. **Remove the else branch** that previously handled the `%W` check when `mysql_M_is_month_name` was false

## Key Code Location

File: `src/Functions/formatDateTime.cpp`
Function: `containsOnlyFixedWidthMySQLFormatters`

Look for:
- `variable_width_formatter = {'W'}` - a separate array with just `%W`
- `variable_width_formatter_M_is_month_name = {'W', 'M'}` - the array that incorrectly includes `%W`
- The logic inside the format string parsing loop that checks for `%W` in different branches

## Expected Behavior After Fix

The `%W` formatter should always be recognized as variable-length, meaning:
- `containsOnlyFixedWidthMySQLFormatters` returns `false` for any format string containing `%W`
- This happens regardless of the `mysql_M_is_month_name` setting

## Testing Your Fix

The fix can be verified by checking the structure of the code:
1. `variable_width_formatter_M_is_month_name` should only contain `'M'` (not `'W'`)
2. The unconditional `%W` check should appear before the `mysql_M_is_month_name` check
3. The else branch containing the old `%W` check should be removed
