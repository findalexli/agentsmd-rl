# Fix formatDateTime %W Variable-Width Formatter Bug

## Problem

The `formatDateTime` function in ClickHouse has a bug where the `%W` formatter (weekday name, e.g., "Monday") is not consistently treated as a variable-width formatter.

When the setting `formatdatetime_parsedatetime_m_is_month_name` is enabled (set to 1), `%W` is incorrectly treated as fixed-width. This causes issues because weekday names have variable lengths (e.g., "Wednesday" is 9 characters, "Sunday" is 6 characters).

## Location

The bug is in the `containsOnlyFixedWidthMySQLFormatters` function in:
- `src/Functions/formatDateTime.cpp`

## What You Need to Do

1. Locate the `containsOnlyFixedWidthMySQLFormatters` function
2. Understand how the variable-width formatter arrays work:
   - `variable_width_formatter` contains formatters that are always variable-width
   - `variable_width_formatter_M_is_month_name` contains formatters that are variable-width only when `mysql_M_is_month_name` is true
3. Fix the logic so that `%W` is always detected as variable-width, regardless of the `mysql_M_is_month_name` setting

## Key Insight

The current code checks for `%W` inside an `else` clause that only executes when `mysql_M_is_month_name` is false AND `mysql_e_with_space_padding` is false. When `mysql_M_is_month_name` is true, `%W` falls through to a different code path that doesn't check for it.

The fix should ensure `%W` is checked for in all cases, not just when certain settings are disabled.

## Testing

The test file `04077_formatdatetime_w_is_a_variable_length_formatter.sql` shows the expected behavior - the output should be weekday names followed by day numbers, and this should work consistently regardless of the various formatdatetime settings.

Expected output for `formatDateTime(d, '%W %d')`:
- Monday 06
- Tuesday 07
- Wednesday 08
- etc.

The weekday name should be properly formatted as a variable-length string in all cases.
