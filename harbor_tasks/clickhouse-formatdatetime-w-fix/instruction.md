# Task: Fix formatDateTime %W Formatter Bug

## Problem Description

The `formatDateTime` function in ClickHouse has a bug where the `%W` formatter (which outputs weekday names like "Monday", "Tuesday", etc.) is inconsistently treated as variable-width depending on other formatting settings.

### Bug Details

In the `containsOnlyFixedWidthMySQLFormatters` function in `src/Functions/formatDateTime.cpp`:

- `%W` should ALWAYS be treated as variable-length because weekday names have different lengths (e.g., "Monday" vs "Wednesday")
- Currently, `%W` is only treated as variable-width when `mysql_M_is_month_name` is false
- When `mysql_M_is_month_name` is true, the code incorrectly treats `%W` as fixed-width

This causes incorrect behavior when:
- Using `%W` in format strings
- With `formatdatetime_parsedatetime_m_is_month_name = 1` setting

### Expected Behavior

The `%W` formatter should be consistently treated as variable-length regardless of other settings like `mysql_M_is_month_name`, `formatdatetime_f_prints_single_zero`, etc.

### Files to Modify

**Primary file:** `src/Functions/formatDateTime.cpp`

Look for the `containsOnlyFixedWidthMySQLFormatters` function. The fix involves:
1. Moving the `%W` check to happen unconditionally BEFORE the `mysql_M_is_month_name` conditional
2. Removing `'W'` from the `variable_width_formatter_M_is_month_name` array (it should only contain `'M'`)
3. Removing the `else` block that previously checked for `%W`

### Testing

The PR includes test files that verify the fix works with various combinations of settings:
- `formatdatetime_parsedatetime_m_is_month_name` (both 0 and 1)
- `formatdatetime_f_prints_single_zero`
- `formatdatetime_f_prints_scale_number_of_digits`
- `formatdatetime_format_without_leading_zeros`

You can verify your fix by checking that:
1. The `variable_width_formatter_M_is_month_name` array only contains `'M'` (not `'W'`)
2. There's an early check for `variable_width_formatter` (which includes `'W'`) before the `mysql_M_is_month_name` conditional
3. The `else` block with the `%W` check has been removed

### Example Test Query

```sql
SELECT formatDateTime(toDate('2026-04-06'), '%W %d')
SETTINGS formatdatetime_parsedatetime_m_is_month_name = 1
```

This should correctly output "Monday 06" regardless of the `mysql_M_is_month_name` setting.
