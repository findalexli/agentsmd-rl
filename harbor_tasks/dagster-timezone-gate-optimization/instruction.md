# Optimize Timezone Conversion Performance in Scheduler

## Problem

The scheduler's hourly cron iteration is slow because it performs expensive timezone-aware datetime conversions for every iteration, even when the timezone offset has no minute component. This affects any deployment using timezones like UTC, Europe/Berlin, America/New_York, Asia/Tokyo, and similar.

## Goal

Optimize the scheduler so that timezones with only whole-hour UTC offsets (e.g., UTC+0, UTC+1, UTC-5) use a fast path that avoids expensive datetime conversions. Timezones with non-zero minute offsets (e.g., UTC+5:45, UTC+5:30, UTC+6:30) should still work correctly but may use a more precise calculation.

## API Requirements

### New Helper Function: `has_nonzero_minute_offset`

Create a function `has_nonzero_minute_offset(tz_str: str) -> bool` that:
- Takes a timezone string (e.g., `"UTC"`, `"Asia/Kathmandu"`) and returns `True` if the timezone has a non-zero minute component in its UTC offset, `False` otherwise
- Must be cached (e.g., using `functools.cache` or equivalent) so that repeated calls with the same timezone string avoid redundant computation
- Must be importable from `dagster._utils.schedules`

Timezones that should return `False` (whole-hour offsets only):
- `UTC`, `Europe/Berlin`, `Europe/London`, `America/New_York`, `America/Los_Angeles`, `Asia/Tokyo`, `Australia/Sydney`

Timezones that should return `True` (non-zero minute offset):
- `Asia/Kathmandu` (UTC+5:45), `Asia/Kolkata` (UTC+5:30), `Asia/Colombo` (UTC+5:30), `Asia/Yangon` (UTC+6:30), `Australia/Adelaide` (UTC+10:30 or +9:30 DST), `America/St_Johns` (UTC-3:30 or -2:30 DST), `Pacific/Chatham` (UTC+12:45 or +13:45 DST), `Asia/Tehran` (UTC+3:30 historically), `Indian/Cocos` (UTC+6:30), `Australia/Eucla` (UTC+8:45)

### New Parameter: `use_timezone_minute_resolution`

The `_find_hourly_schedule_time` function must accept a new parameter `use_timezone_minute_resolution: bool` that:
- When `False`, uses a fast arithmetic path to compute the current minute (avoiding timezone-aware datetime conversion)
- When `True`, uses the full timezone-aware datetime conversion to get the minute
- This parameter should also be accepted and propagated through `_find_schedule_time` (with a default of `False`)

The `cron_string_iterator` function should determine the appropriate value for this parameter based on the execution timezone and pass it through to `_find_schedule_time`.

## Expected Behavior

After optimization:
- Hourly cron schedules must produce correct results for all timezones
- Timezones with only whole-hour offsets should use the fast path
- Timezones with minute-offset components must still be handled correctly
- The iterator should work correctly in both ascending and descending directions

## Verification

After making changes:
1. The scheduler must pass all existing tests: `make ruff`, `make check_ruff`
2. The schedule iterator tests must pass: `pytest dagster_tests/scheduler_tests/test_schedule_iterator.py dagster_tests/scheduler_tests/test_scheduler_utils.py`
3. The core cron string iterator tests must pass: `pytest dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_cron_iterator_always_advances dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_cron_iterator_leap_day dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_invalid_cron_strings dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_get_smallest_cron_interval_basic`

## File to Modify

`python_modules/dagster/dagster/_utils/schedules.py`

## Notes

- The module must continue to export `cron_string_iterator`, `_find_hourly_schedule_time`, `_find_schedule_time`, and `has_nonzero_minute_offset`
- Any new functions added should work correctly with the existing schedule iteration logic
- The solution must not break any existing functionality for non-hourly schedules
