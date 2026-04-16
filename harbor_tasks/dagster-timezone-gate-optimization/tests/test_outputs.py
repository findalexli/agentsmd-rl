"""Tests for timezone optimization gate in schedules.py."""

import datetime
import sys
from typing import Optional

# Add dagster to path
sys.path.insert(0, "/workspace/dagster/python_modules/dagster")

import pytest

REPO = "/workspace/dagster"
SCHEDULES_PATH = f"{REPO}/python_modules/dagster/dagster/_utils/schedules.py"


def test_has_nonzero_minute_offset_function_exists():
    """The has_nonzero_minute_offset function must exist and be cached."""
    from dagster._utils.schedules import has_nonzero_minute_offset

    # Function should exist and be callable
    assert callable(has_nonzero_minute_offset)

    # Should have functools.cache (lru_cache in Python < 3.9)
    assert hasattr(has_nonzero_minute_offset, 'cache_info')


def test_has_nonzero_minute_offset_returns_false_for_hour_only_timezones():
    """Timezones with only hour offsets should return False."""
    from dagster._utils.schedules import has_nonzero_minute_offset

    hour_only_timezones = [
        "UTC",
        "Europe/Berlin",
        "Europe/London",
        "America/New_York",
        "America/Los_Angeles",
        "Asia/Tokyo",
        "Australia/Sydney",
    ]

    for tz_str in hour_only_timezones:
        result = has_nonzero_minute_offset(tz_str)
        assert result is False, f"Expected False for {tz_str}, got {result}"


def test_has_nonzero_minute_offset_returns_true_for_minute_offset_timezones():
    """Timezones with minute offsets should return True."""
    from dagster._utils.schedules import has_nonzero_minute_offset

    minute_offset_timezones = [
        "Asia/Kathmandu",    # UTC+5:45
        "Asia/Kolkata",      # UTC+5:30
        "Asia/Colombo",      # UTC+5:30
        "Asia/Yangon",       # UTC+6:30
        "Australia/Adelaide", # UTC+10:30 (or +9:30 depending on DST)
        "America/St_Johns",  # UTC-3:30 (or -2:30 depending on DST)
        "Pacific/Chatham",   # UTC+12:45 (or +13:45 depending on DST)
        "Asia/Tehran",       # UTC+3:30 (historically)
        "Indian/Cocos",      # UTC+6:30
        "Australia/Eucla",   # UTC+8:45
    ]

    for tz_str in minute_offset_timezones:
        result = has_nonzero_minute_offset(tz_str)
        assert result is True, f"Expected True for {tz_str}, got {result}"


def test_cron_string_iterator_with_utc_timezone():
    """Hourly cron iterator should work correctly with UTC."""
    from dagster._utils.schedules import cron_string_iterator

    # Start from a time not on the boundary (12:05) so we get meaningful results
    start = datetime.datetime(2024, 1, 1, 12, 5, 0, tzinfo=datetime.timezone.utc)
    start_timestamp = int(start.timestamp())

    iterator = cron_string_iterator(
        start_timestamp=start_timestamp,
        cron_string="0 * * * *",  # Hourly at minute 0
        execution_timezone="UTC",
    )

    # Get next 5 iterations - cron_string_iterator yields datetime objects
    times = []
    for _ in range(5):
        dt = next(iterator)
        times.append(dt)

    # Should be at hour boundaries (starting at 13:00 since we're at 12:05)
    expected_hours = [13, 14, 15, 16, 17]
    for i, (actual, expected_hour) in enumerate(zip(times, expected_hours)):
        assert actual.minute == 0, f"Iteration {i}: Expected minute 0, got {actual.minute}"
        assert actual.hour == expected_hour % 24, f"Iteration {i}: Expected hour {expected_hour % 24}, got {actual.hour}"


def test_cron_string_iterator_with_kathmandu_timezone():
    """Hourly cron iterator should work correctly with Asia/Kathmandu (UTC+5:45)."""
    import pytz
    from dagster._utils.schedules import cron_string_iterator

    tz = pytz.timezone("Asia/Kathmandu")
    start = tz.localize(datetime.datetime(2024, 1, 1, 12, 0, 0))
    start_timestamp = int(start.timestamp())

    iterator = cron_string_iterator(
        start_timestamp=start_timestamp,
        cron_string="0 * * * *",  # Hourly at minute 0
        execution_timezone="Asia/Kathmandu",
    )

    # Get next 5 iterations - cron_string_iterator yields datetime objects
    times = []
    for _ in range(5):
        dt = next(iterator)
        times.append(dt)

    # Should be at hour boundaries in Kathmandu time
    for i, actual in enumerate(times):
        assert actual.minute == 0, f"Iteration {i}: Expected minute 0, got {actual.minute}"
        assert str(actual.tzinfo) == "Asia/Kathmandu", f"Iteration {i}: Wrong timezone {actual.tzinfo}"


def test_cron_string_iterator_ascending_vs_descending():
    """Iterator should work in both ascending and descending directions."""
    from dagster._utils.schedules import cron_string_iterator

    # Start at 12:05 (not on boundary) so we get meaningful results
    start = datetime.datetime(2024, 1, 1, 12, 5, 0, tzinfo=datetime.timezone.utc)
    start_timestamp = int(start.timestamp())

    # Test ascending (default) - should go forward to 13:00
    asc_iterator = cron_string_iterator(
        start_timestamp=start_timestamp,
        cron_string="0 * * * *",
        execution_timezone="UTC",
        ascending=True,
    )
    first_asc = next(asc_iterator)  # cron_string_iterator yields datetime objects
    assert first_asc > start, f"Ascending should go forward: {first_asc} > {start}"
    assert first_asc.hour == 13, f"Expected hour 13, got {first_asc.hour}"

    # Test descending - should go backward to 12:00
    desc_iterator = cron_string_iterator(
        start_timestamp=start_timestamp,
        cron_string="0 * * * *",
        execution_timezone="UTC",
        ascending=False,
    )
    first_desc = next(desc_iterator)  # cron_string_iterator yields datetime objects
    assert first_desc < start, f"Descending should go backward: {first_desc} < {start}"
    assert first_desc.hour == 12, f"Expected hour 12, got {first_desc.hour}"


def test_cron_string_iterator_with_various_hourly_patterns():
    """Test with various hourly cron patterns."""
    from dagster._utils.schedules import cron_string_iterator

    start = datetime.datetime(2024, 1, 1, 12, 30, 0, tzinfo=datetime.timezone.utc)
    start_timestamp = int(start.timestamp())

    patterns = [
        "0 * * * *",     # Every hour at minute 0
        "30 * * * *",    # Every hour at minute 30
        "*/15 * * * *",  # Every 15 minutes
    ]

    for pattern in patterns:
        for tz_str in ["UTC", "Asia/Kathmandu"]:
            iterator = cron_string_iterator(
                start_timestamp=start_timestamp,
                cron_string=pattern,
                execution_timezone=tz_str,
            )
            # Just verify we can get iterations without error (yields datetime objects)
            for _ in range(3):
                dt = next(iterator)
                assert isinstance(dt, datetime.datetime), f"Should yield datetime for {pattern} in {tz_str}"


def test_find_hourly_schedule_time_accepts_new_parameter():
    """_find_hourly_schedule_time should accept the new use_timezone_minute_resolution parameter."""
    import pytz
    from dagster._utils.schedules import _find_hourly_schedule_time

    tz_utc = pytz.timezone("UTC")
    start = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz_utc)

    # Test with use_timezone_minute_resolution=False
    result1 = _find_hourly_schedule_time(
        minutes=[0],
        date=start,
        ascending=True,
        already_on_boundary=True,
        use_timezone_minute_resolution=False,
    )
    assert isinstance(result1, datetime.datetime)

    # Test with use_timezone_minute_resolution=True
    result2 = _find_hourly_schedule_time(
        minutes=[0],
        date=start,
        ascending=True,
        already_on_boundary=True,
        use_timezone_minute_resolution=True,
    )
    assert isinstance(result2, datetime.datetime)


def test_make_ruff_linting():
    """Code should pass ruff linting (pass-to-pass check)."""
    import subprocess

    result = subprocess.run(
        ["make", "ruff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Ruff linting failed:\n{result.stderr}\n{result.stdout}"


def test_repo_check_ruff():
    """Repo code passes ruff linting and format checks (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["make", "check_ruff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_schedule_iterator_tests():
    """Repo's schedule iterator tests pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "dagster_tests/scheduler_tests/test_schedule_iterator.py",
            "dagster_tests/scheduler_tests/test_scheduler_utils.py",
            "-v", "--tb=short",
        ],
        cwd=f"{REPO}/python_modules/dagster",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Schedule iterator tests failed:\n{result.stderr[-500:]}"


def test_repo_cron_string_core_tests():
    """Repo's core cron string iterator tests pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_cron_iterator_always_advances",
            "dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_cron_iterator_leap_day",
            "dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_invalid_cron_strings",
            "dagster_tests/scheduler_tests/test_cron_string_iterator.py::test_get_smallest_cron_interval_basic",
            "-v", "--tb=short",
        ],
        cwd=f"{REPO}/python_modules/dagster",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Cron string core tests failed:\n{result.stderr[-500:]}"


def test_module_imports():
    """The schedules module should import without errors."""
    import dagster._utils.schedules as schedules_module

    # Key functions should be available
    assert hasattr(schedules_module, 'cron_string_iterator')
    assert hasattr(schedules_module, '_find_hourly_schedule_time')
    assert hasattr(schedules_module, '_find_schedule_time')
    assert hasattr(schedules_module, 'has_nonzero_minute_offset')
