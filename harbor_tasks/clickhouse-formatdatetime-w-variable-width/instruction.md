# Fix formatDateTime %W Variable-Width Detection

## Problem

The `%W` formatter (weekday name) in ClickHouse's `formatDateTime` function is not consistently detected as variable-width across all configuration settings.

When the setting `formatdatetime_parsedatetime_m_is_month_name` is enabled (set to 1), the function `containsOnlyFixedWidthMySQLFormatters` returns `true` for format strings containing `%W`, incorrectly indicating they are fixed-width. Weekday names have variable lengths (e.g., "Wednesday" is 9 characters, "Monday" is 6 characters).

## Expected Behavior

The function `containsOnlyFixedWidthMySQLFormatters` should return `false` when the format string contains `%W`, regardless of the `mysql_M_is_month_name` setting value.

Specifically:
- When called with format `"%W"`, `mysql_M_is_month_name=true`, `mysql_format_ckl_without_leading_zeros=false`, `mysql_e_with_space_padding=false` - should return `false` (variable-width detected)
- When called with format `"%W"`, `mysql_M_is_month_name=false`, `mysql_format_ckl_without_leading_zeros=false`, `mysql_e_with_space_padding=false` - should return `false` (variable-width detected)

The `%M` formatter should continue to be variable-width only when `mysql_M_is_month_name=true`.

## Files to Modify

The relevant arrays in the source code are:
- `variable_width_formatter` - formatters that are always variable-width
- `variable_width_formatter_M_is_month_name` - formatters that are variable-width when `mysql_M_is_month_name` is true
- `variable_width_formatter_leading_zeros` - formatters related to leading zero settings
- `variable_width_formatter_e_with_space_padding` - formatters related to space padding settings

The fix should ensure `%W` is always detected as variable-width, independent of the conditional flag checks for other formatters.
