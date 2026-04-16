"""
Tests for airflow-dag-startdate-tz-overflow task.

Verifies that start_date values in example DAGs survive conversion to
non-UTC timezones without raising OverflowError.
"""

import ast
import datetime
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path("/workspace/airflow")
EXAMPLE_DAGS = REPO / "airflow-core" / "src" / "airflow" / "example_dags"


def _extract_start_dates(filepath: Path) -> list[datetime.datetime]:
    """Parse a Python file with AST and evaluate all start_date keyword
    arguments found in any call expression.  Returns the evaluated
    datetime objects so callers can assert on their *values* rather than
    on source text."""
    source = filepath.read_text()
    tree = ast.parse(source)

    namespace = {"datetime": datetime, "__builtins__": {}}
    results: list[datetime.datetime] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg != "start_date":
                continue
            expr = ast.Expression(body=kw.value)
            code = compile(expr, str(filepath), "eval")
            val = eval(code, namespace)  # noqa: S307
            if isinstance(val, datetime.datetime):
                results.append(val)

    return results


# ------------------------------------------------------------------
# fail-to-pass tests
# ------------------------------------------------------------------


def test_inlet_event_extra_start_date_tz_conversion():
    """start_date values in example_inlet_event_extra.py must survive
    conversion to non-UTC timezones without OverflowError."""
    filepath = EXAMPLE_DAGS / "example_inlet_event_extra.py"
    start_dates = _extract_start_dates(filepath)

    assert len(start_dates) >= 2, (
        f"Expected at least 2 start_dates in {filepath.name}, "
        f"found {len(start_dates)}"
    )

    for sd in start_dates:
        for tz_name in ("Asia/Shanghai", "Asia/Tokyo", "Australia/Sydney"):
            script = (
                "import datetime\n"
                "from zoneinfo import ZoneInfo\n"
                f"sd = {sd!r}\n"
                "if sd.tzinfo is None:\n"
                "    sd = sd.replace(tzinfo=datetime.timezone.utc)\n"
                f"converted = sd.astimezone(ZoneInfo('{tz_name}'))\n"
                "assert converted.year >= 1970\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, (
                f"TZ conversion to {tz_name} failed for start_date={sd}:\n"
                f"{result.stderr}"
            )


def test_outlet_event_extra_start_date_tz_conversion():
    """start_date values in example_outlet_event_extra.py must survive
    conversion to non-UTC timezones without OverflowError."""
    filepath = EXAMPLE_DAGS / "example_outlet_event_extra.py"
    start_dates = _extract_start_dates(filepath)

    assert len(start_dates) >= 3, (
        f"Expected at least 3 start_dates in {filepath.name}, "
        f"found {len(start_dates)}"
    )

    for sd in start_dates:
        for tz_name in ("Asia/Shanghai", "Europe/Moscow", "Pacific/Auckland"):
            script = (
                "import datetime\n"
                "from zoneinfo import ZoneInfo\n"
                f"sd = {sd!r}\n"
                "if sd.tzinfo is None:\n"
                "    sd = sd.replace(tzinfo=datetime.timezone.utc)\n"
                f"converted = sd.astimezone(ZoneInfo('{tz_name}'))\n"
                "assert converted.year >= 1970\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, (
                f"TZ conversion to {tz_name} failed for start_date={sd}:\n"
                f"{result.stderr}"
            )


def test_start_date_is_timezone_aware():
    """start_date values must carry timezone information."""
    files = [
        EXAMPLE_DAGS / "example_inlet_event_extra.py",
        EXAMPLE_DAGS / "example_outlet_event_extra.py",
    ]

    for filepath in files:
        start_dates = _extract_start_dates(filepath)
        assert len(start_dates) > 0, f"No start_dates found in {filepath.name}"
        for sd in start_dates:
            assert sd.tzinfo is not None, (
                f"start_date in {filepath.name} lacks timezone info: {sd!r}"
            )


def test_start_date_uses_valid_epoch():
    """start_date year must be >= 1970.  Using a very early year (e.g.
    year 1 from datetime.min) causes overflow during timezone conversion."""
    files = [
        EXAMPLE_DAGS / "example_inlet_event_extra.py",
        EXAMPLE_DAGS / "example_outlet_event_extra.py",
    ]

    for filepath in files:
        start_dates = _extract_start_dates(filepath)
        assert len(start_dates) > 0, f"No start_dates found in {filepath.name}"
        for sd in start_dates:
            assert sd.year >= 1970, (
                f"start_date in {filepath.name} has year={sd.year}, expected >= 1970"
            )


# ------------------------------------------------------------------
# pass-to-pass tests
# ------------------------------------------------------------------


def test_python_syntax_valid():
    """Modified DAG files must have valid Python syntax."""
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
    """ruff check must pass on modified DAG files."""
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
    """ruff format --check must pass on modified DAG files."""
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
