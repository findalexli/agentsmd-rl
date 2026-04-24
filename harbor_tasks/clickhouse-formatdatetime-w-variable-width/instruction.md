# Fix formatDateTime %W Variable-Width Detection

## Problem

The `%W` formatter (weekday name) in ClickHouse's `formatDateTime` function is not consistently detected as variable-width.

When the `formatdatetime_parsedatetime_m_is_month_name` setting is enabled, the function that checks for fixed-width formatters incorrectly returns `true` for format strings containing `%W`, treating weekday names as fixed-width. Weekday names have variable lengths (e.g., "Wednesday" vs "Monday").

## Symptom

When using `formatDateTime` with a format string containing `%W`:
- The formatter is sometimes treated as fixed-width when it should be variable-width
- This affects output alignment/padding in certain configuration combinations
- The issue specifically manifests when `formatdatetime_parsedatetime_m_is_month_name = 1`

## Expected Behavior

The `%W` formatter should always be treated as variable-width, regardless of any configuration settings. Weekday names have different lengths:
- "Monday" (6 chars)
- "Tuesday" (7 chars)
- "Wednesday" (9 chars)
- "Thursday" (8 chars)
- "Friday" (6 chars)
- "Saturday" (8 chars)
- "Sunday" (6 chars)

The function that determines if a format string contains only fixed-width formatters should return `false` (indicating variable-width) when the format string contains `%W`.

## Related Context

The `%M` formatter (month name) has existing behavior where it is:
- Variable-width when `formatdatetime_parsedatetime_m_is_month_name = 1`
- Fixed-width when `formatdatetime_parsedatetime_m_is_month_name = 0`

This `%M` behavior should remain unchanged.

## Source File

The relevant function is in `src/Functions/formatDateTime.cpp` within the `FunctionFormatDateTimeImpl` class. Look for the logic that determines whether formatters are fixed-width or variable-width.

## Reproduction

The bug can be verified by checking the return value of the width-checking function when passed a format string containing `%W` with different configuration flag combinations.
