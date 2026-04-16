# Fix formatDateTime %W Variable-Width Detection

## Problem

The `%W` formatter (weekday name) in ClickHouse's `formatDateTime` function is not consistently detected as variable-width.

When certain settings are configured, the function `containsOnlyFixedWidthMySQLFormatters` incorrectly returns `true` for format strings containing `%W`, indicating they are fixed-width. Weekday names have variable lengths (e.g., "Wednesday" vs "Monday").

## Expected Behavior

The function `containsOnlyFixedWidthMySQLFormatters` should return `false` (indicating variable-width) when the format string contains `%W`, regardless of configuration settings.

For example:
- `containsOnlyFixedWidthMySQLFormatters("%W", ...)` should return `false` when `mysql_M_is_month_name=true`
- `containsOnlyFixedWidthMySQLFormatters("%W", ...)` should return `false` when `mysql_M_is_month_name=false`
- The `%M` formatter behavior should remain unchanged: variable-width when `mysql_M_is_month_name=true`, fixed-width otherwise.

## Source File

The function `containsOnlyFixedWidthMySQLFormatters` lives in:
- File: `src/Functions/formatDateTime.cpp`
- Location: within the `FunctionFormatDateTimeImpl` class implementation
