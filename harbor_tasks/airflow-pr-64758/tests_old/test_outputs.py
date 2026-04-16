"""
Tests for airflow-dag-startdate-tz-overflow task.

This verifies that the start_date values in example DAGs can be converted to
non-UTC timezones without causing an OverflowError.

The bug: Using datetime.datetime.min as start_date causes an overflow when
Airflow tries to convert it to a non-UTC timezone (e.g., Asia/Shanghai).

The fix: Use datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) instead.
"""

import datetime
import re
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path("/workspace/airflow")
EXAMPLE_DAGS = REPO / "airflow-core" / "src" / "airflow" / "example_dags"


def extract_start_dates_from_file(filepath: Path) -> list[datetime.datetime]:
    """
    Extract and evaluate start_date expressions from a DAG file.

    This parses the Python file and extracts start_date=<expr> patterns,
    then evaluates them in a context with only the datetime module.
    """
    content = filepath.read_text()

    # Find all start_date=<expression> patterns
    # Handle both simple (datetime.datetime.min) and complex expressions
    # (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc))
    start_dates = []

    # Pattern 1: datetime.datetime.min (simple attribute access)
    pattern_simple = r'start_date\s*=\s*(datetime\.datetime\.min)'
    for match in re.findall(pattern_simple, content):
        try:
            value = eval(match, {"datetime": datetime, "__builtins__": {}})
            if isinstance(value, datetime.datetime):
                start_dates.append(value)
        except Exception:
            pass

    # Pattern 2: datetime.datetime(...) with arguments (may contain nested parens)
    # Find start_date=datetime.datetime( and then match balanced parentheses
    pattern_func = r'start_date\s*=\s*(datetime\.datetime\([^)]*\))'
    for match in re.findall(pattern_func, content):
        try:
            value = eval(match, {"datetime": datetime, "__builtins__": {}})
            if isinstance(value, datetime.datetime):
                start_dates.append(value)
        except Exception:
            pass

    return start_dates


def test_inlet_event_extra_start_date_tz_conversion():
    """
    Test that start_date in example_inlet_event_extra.py can be converted
    to non-UTC timezones without OverflowError.

    fail_to_pass: On the base commit, datetime.datetime.min causes overflow.
    """
    filepath = EXAMPLE_DAGS / "example_inlet_event_extra.py"
    start_dates = extract_start_dates_from_file(filepath)

    assert len(start_dates) >= 2, f"Expected at least 2 start_dates, found {len(start_dates)}"

    # Test conversion to various non-UTC timezones
    # These timezones have positive offsets that would push datetime.min before year 1
    timezones = [
        ZoneInfo("Asia/Shanghai"),  # UTC+8
        ZoneInfo("Asia/Tokyo"),     # UTC+9
        ZoneInfo("Australia/Sydney"),  # UTC+10/11
    ]

    for sd in start_dates:
        for tz in timezones:
            # Ensure datetime is timezone-aware before conversion
            if sd.tzinfo is None:
                sd = sd.replace(tzinfo=datetime.timezone.utc)
            # This should not raise OverflowError
            converted = sd.astimezone(tz)
            assert converted is not None
            # Verify the year is reasonable (not overflow)
            assert converted.year >= 1970, f"Unexpected year {converted.year} after TZ conversion"


def test_outlet_event_extra_start_date_tz_conversion():
    """
    Test that start_date in example_outlet_event_extra.py can be converted
    to non-UTC timezones without OverflowError.

    fail_to_pass: On the base commit, datetime.datetime.min causes overflow.
    """
    filepath = EXAMPLE_DAGS / "example_outlet_event_extra.py"
    start_dates = extract_start_dates_from_file(filepath)

    assert len(start_dates) >= 3, f"Expected at least 3 start_dates, found {len(start_dates)}"

    # Test conversion to various non-UTC timezones
    timezones = [
        ZoneInfo("Asia/Shanghai"),  # UTC+8 - the original bug report timezone
        ZoneInfo("Europe/Moscow"),  # UTC+3
        ZoneInfo("Pacific/Auckland"),  # UTC+12/13
    ]

    for sd in start_dates:
        for tz in timezones:
            if sd.tzinfo is None:
                sd = sd.replace(tzinfo=datetime.timezone.utc)
            converted = sd.astimezone(tz)
            assert converted is not None
            assert converted.year >= 1970, f"Unexpected year {converted.year} after TZ conversion"


def test_start_date_is_timezone_aware():
    """
    Test that start_date values have timezone info attached.

    fail_to_pass: On base commit, datetime.datetime.min has no tzinfo.
    """
    files = [
        EXAMPLE_DAGS / "example_inlet_event_extra.py",
        EXAMPLE_DAGS / "example_outlet_event_extra.py",
    ]

    for filepath in files:
        start_dates = extract_start_dates_from_file(filepath)
        for sd in start_dates:
            assert sd.tzinfo is not None, (
                f"start_date in {filepath.name} should have timezone info, "
                f"got {sd!r}"
            )


def test_start_date_uses_valid_epoch():
    """
    Test that start_date values use a valid epoch (not datetime.min).

    fail_to_pass: On base commit, start_date is datetime.min (year 1).
    """
    files = [
        EXAMPLE_DAGS / "example_inlet_event_extra.py",
        EXAMPLE_DAGS / "example_outlet_event_extra.py",
    ]

    for filepath in files:
        start_dates = extract_start_dates_from_file(filepath)
        for sd in start_dates:
            # datetime.min has year=1, which causes overflow issues
            # The fix uses 1970-01-01 which is the Unix epoch
            assert sd.year >= 1970, (
                f"start_date in {filepath.name} should not use datetime.min "
                f"(year={sd.year}), expected year >= 1970"
            )


def test_python_syntax_valid():
    """
    Test that the modified DAG files have valid Python syntax.

    pass_to_pass: Should pass on both base and fixed commits.
    """
    files = [
        EXAMPLE_DAGS / "example_inlet_event_extra.py",
        EXAMPLE_DAGS / "example_outlet_event_extra.py",
    ]

    for filepath in files:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(filepath)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"Syntax error in {filepath.name}:\n{result.stderr}"
        )


def test_ruff_lint():
    """
    Test that ruff linting passes on the modified DAG files.

    pass_to_pass: Airflow CI uses ruff for linting. From AGENTS.md:
    "Always format and check Python files with ruff immediately after writing or editing them."
    """
    files = [
        str(EXAMPLE_DAGS / "example_inlet_event_extra.py"),
        str(EXAMPLE_DAGS / "example_outlet_event_extra.py"),
    ]

    result = subprocess.run(
        ["ruff", "check"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"ruff check failed:\n{result.stdout}\n{result.stderr}"
    )


def test_ruff_format():
    """
    Test that ruff formatting passes on the modified DAG files.

    pass_to_pass: Airflow CI uses ruff for formatting. From AGENTS.md:
    "Always format and check Python files with ruff immediately after writing or editing them."
    """
    files = [
        str(EXAMPLE_DAGS / "example_inlet_event_extra.py"),
        str(EXAMPLE_DAGS / "example_outlet_event_extra.py"),
    ]

    result = subprocess.run(
        ["ruff", "format", "--check"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"ruff format --check failed:\n{result.stdout}\n{result.stderr}"
    )
