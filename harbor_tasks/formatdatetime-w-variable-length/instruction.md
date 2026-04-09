# Fix formatDateTime %W Variable-Length Formatter Bug

## Problem

The `formatDateTime` function in ClickHouse has a bug where the `%W` formatter (weekday name) is not consistently treated as a variable-length formatter. The function `containsOnlyFixedWidthMySQLFormatters` in `src/Functions/formatDateTime.cpp` determines if a format string contains only fixed-width formatters.

The bug: `%W` is only treated as variable-length in some code paths but not others. Specifically, the check for `%W` being variable-length only happens in an `else` branch, but it should happen unconditionally for all code paths.

This causes incorrect behavior when using `formatDateTime` with the `%W` formatter combined with certain settings like `formatdatetime_parsedatetime_m_is_month_name`.

## Files to Modify

- `src/Functions/formatDateTime.cpp`

## Hints

1. Look at the function `containsOnlyFixedWidthMySQLFormatters` around line 863
2. The `variable_width_formatter` array contains `'W'` (weekday name)
3. The `variable_width_formatter_M_is_month_name` array should probably only contain `'M'`
4. The check for `%W` should happen unconditionally before the `if (mysql_M_is_month_name)` conditional, not just in the `else` branch
5. Follow the Allman brace style (opening brace on new line) used in the rest of the codebase

## Expected Behavior

After the fix, `%W` should be treated as a variable-length formatter regardless of the value of `mysql_M_is_month_name` or other settings. The code should check for `%W` unconditionally before the conditional branch.
