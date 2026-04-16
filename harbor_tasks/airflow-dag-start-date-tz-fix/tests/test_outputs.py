"""Test that the PR fix is correctly applied — behavioral tests.

These tests parse the DAG files with AST, extract start_date values from
DAG() calls, eval them into actual datetime objects, and assert on their
runtime properties (timezone awareness, safe conversion, not datetime.min).
This is agnostic to HOW the fix is spelled in source — any correct UTC-aware
epoch datetime that converts safely will pass.
"""

import ast
import datetime
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/airflow")
INLET_FILE = (
    REPO / "airflow-core" / "src" / "airflow" / "example_dags" / "example_inlet_event_extra.py"
)
OUTLET_FILE = (
    REPO / "airflow-core" / "src" / "airflow" / "example_dags" / "example_outlet_event_extra.py"
)


def _ensure_ruff():
    """Ensure ruff is installed for CI checks."""
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff", "--quiet"], check=True
        )


_ensure_ruff()


def _extract_start_dates(filepath):
    """Parse a Python file and evaluate every start_date kwarg in DAG() calls.

    Walks the AST looking for with DAG(..., start_date=<expr>, ...): blocks,
    unparses the <expr>, and evals it with datetime available so we get a
    real datetime object.  Returns a list of evaluated datetime values (one per
    DAG definition found).
    """
    source = filepath.read_text()
    tree = ast.parse(source)

    # Build an eval namespace that mirrors what the file itself can reference.
    eval_ns = {"__builtins__": {}, "datetime": datetime}
    # Also support alternative fixes that add "from datetime import timezone"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            for alias in node.names:
                if alias.name == "timezone":
                    eval_ns["timezone"] = datetime.timezone

    start_dates = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            ctx = item.context_expr
            if not isinstance(ctx, ast.Call):
                continue
            func = ctx.func
            if not (isinstance(func, ast.Name) and func.id == "DAG"):
                continue
            for kw in ctx.keywords:
                if kw.arg != "start_date":
                    continue
                expr = ast.unparse(kw.value)
                try:
                    val = eval(expr, eval_ns)  # noqa: S307
                except Exception as exc:
                    raise AssertionError(
                        f"Could not evaluate start_date expression in {filepath.name}: {exc}"
                    ) from exc
                start_dates.append(val)

    return start_dates


# Pass-to-pass tests


def test_inlet_file_exists():
    """The inlet event extra example DAG file exists."""
    assert INLET_FILE.exists(), f"File not found: {INLET_FILE}"


def test_outlet_file_exists():
    """The outlet event extra example DAG file exists."""
    assert OUTLET_FILE.exists(), f"File not found: {OUTLET_FILE}"


def test_inlet_file_valid_python():
    """The inlet file is valid Python syntax."""
    try:
        ast.parse(INLET_FILE.read_text())
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {INLET_FILE}: {e}") from e


def test_outlet_file_valid_python():
    """The outlet file is valid Python syntax."""
    try:
        ast.parse(OUTLET_FILE.read_text())
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {OUTLET_FILE}: {e}") from e


def test_repo_ruff_check():
    """Ruff linter passes on modified files."""
    r = subprocess.run(
        ["ruff", "check", "--force-exclude", str(INLET_FILE), str(OUTLET_FILE)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Ruff format check passes on modified files."""
    r = subprocess.run(
        ["ruff", "format", "--check", str(INLET_FILE), str(OUTLET_FILE)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Ruff format check failed (files not formatted):\n{r.stdout}\n{r.stderr}"
    )


# Fail-to-pass tests


def test_start_dates_not_datetime_min():
    """No start_date in any DAG equals datetime.datetime.min.

    datetime.datetime.min sits at the absolute boundary of Python datetime
    range, so applying any negative UTC offset pushes it out of range and
    raises OverflowError inside Airflow timezone-conversion logic.
    """
    for filepath in [INLET_FILE, OUTLET_FILE]:
        start_dates = _extract_start_dates(filepath)
        assert len(start_dates) > 0, f"No DAG definitions found in {filepath.name}"
        for i, sd in enumerate(start_dates, 1):
            assert sd != datetime.datetime.min, (
                f"{filepath.name} DAG #{i}: start_date is datetime.datetime.min, "
                "which causes OverflowError during timezone conversion"
            )


def test_start_dates_are_timezone_aware():
    """All start_date values carry timezone information.

    Airflow requires timezone-aware datetimes for start_date so that the
    scheduler can correctly compute execution dates across timezones.
    """
    for filepath in [INLET_FILE, OUTLET_FILE]:
        start_dates = _extract_start_dates(filepath)
        for i, sd in enumerate(start_dates, 1):
            assert sd.tzinfo is not None, (
                f"{filepath.name} DAG #{i}: start_date {sd!r} is timezone-naive; "
                "Airflow requires timezone-aware start_date values"
            )


def test_start_dates_safe_for_timezone_conversion():
    """Every start_date can be converted to common timezones without OverflowError.

    The bug manifested as OverflowError when Airflow scheduler converted the
    start_date to the configured timezone. Any valid fix must produce a
    datetime that survives conversion to offsets ranging from UTC-8 to UTC+9.
    """
    tz_offsets = [
        datetime.timedelta(hours=+9),            # JST
        datetime.timedelta(hours=-8),            # PST
        datetime.timedelta(hours=+1),            # CET
        datetime.timedelta(hours=-5),            # EST
        datetime.timedelta(hours=+5, minutes=30),  # IST
    ]
    for filepath in [INLET_FILE, OUTLET_FILE]:
        start_dates = _extract_start_dates(filepath)
        for i, sd in enumerate(start_dates, 1):
            for offset in tz_offsets:
                tz = datetime.timezone(offset)
                try:
                    converted = sd.astimezone(tz)
                except (OverflowError, ValueError) as exc:
                    raise AssertionError(
                        f"{filepath.name} DAG #{i}: start_date {sd!r} "
                        f"causes {type(exc).__name__} when converting to "
                        f"UTC offset {offset}: {exc}"
                    ) from exc
                assert isinstance(converted, datetime.datetime)


def test_all_five_dags_have_safe_start_dates():
    """Both files together define exactly 5 DAGs, each with a safe start_date.

    Inlet has 2 DAGs, outlet has 3. All 5 must use a start_date that is (a)
    not datetime.min, (b) timezone-aware, and (c) safe under timezone
    conversion.
    """
    inlet_dates = _extract_start_dates(INLET_FILE)
    outlet_dates = _extract_start_dates(OUTLET_FILE)

    assert len(inlet_dates) == 2, (
        f"Expected 2 DAG definitions in {INLET_FILE.name}, found {len(inlet_dates)}"
    )
    assert len(outlet_dates) == 3, (
        f"Expected 3 DAG definitions in {OUTLET_FILE.name}, found {len(outlet_dates)}"
    )

    all_dates = inlet_dates + outlet_dates
    for i, sd in enumerate(all_dates, 1):
        assert sd != datetime.datetime.min, (
            f"DAG #{i} start_date is datetime.datetime.min"
        )
        assert sd.tzinfo is not None, (
            f"DAG #{i} start_date {sd!r} is timezone-naive"
        )
        sd.astimezone(datetime.timezone(datetime.timedelta(hours=-8)))
