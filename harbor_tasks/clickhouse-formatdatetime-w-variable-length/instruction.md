# formatDateTime %W Variable-Length Formatter Bug

## Problem

The `formatDateTime` function in ClickHouse has a bug where the `%W` formatter (which outputs the full weekday name like "Monday") is treated inconsistently depending on the `mysql_M_is_month_name` setting.

When `mysql_M_is_month_name` is enabled, `%W` is incorrectly considered a fixed-width formatter. This causes truncated output for weekday names longer than the shortest form (e.g., "Monday" being cut to "Mond" or similar), and incorrect padding calculations.

The correct behavior is that `%W` should always be treated as variable-length.

## Where to Look

The bug is in `src/Functions/formatDateTime.cpp`, in the `containsOnlyFixedWidthMySQLFormatters` function. This function determines whether a format string contains only fixed-width formatters.

## Files to Modify

- `src/Functions/formatDateTime.cpp` - the `containsOnlyFixedWidthMySQLFormatters` function

## Verification

The following test files must exist in the repository:
- `tests/queries/0_stateless/00718_format_datetime.sql`
- `tests/queries/0_stateless/00718_format_datetime.reference`
- `tests/queries/0_stateless/00719_format_datetime_f_varsize_bug.sql`
- `tests/queries/0_stateless/00719_format_datetime_f_varsize_bug.reference`

After the fix, running `00719_format_datetime_f_varsize_bug.sql` should produce correct output without truncation.

## Notes

- This is a C++ codebase using Allman-style braces (opening brace on new line)
- The function signature is: `static bool containsOnlyFixedWidthMySQLFormatters(std::string_view format, bool mysql_M_is_month_name, bool mysql_format_ckl_without_leading_zeros, bool mysql_e_with_space_padding)`
- C++ style checks must pass after the fix (using the repo's `check_style/check_cpp.sh` and `check_style/various_checks.sh`)