"""Behavioral tests for the word-cloud buildQuery fix (apache/superset#39073).

The runner at /harness/run_buildquery.ts loads the buildQuery TypeScript source
through tsx (with hand-rolled stubs for @superset-ui/core / @apache-superset/core
under /node_modules), exercises it with several formData inputs, and emits a
JSON object describing the resulting orderby / columns for each case. These
Python tests parse that JSON and assert on the observable behavior.
"""
from __future__ import annotations

import functools
import json
import subprocess
from pathlib import Path

HARNESS = Path("/harness")
RUNNER = HARNESS / "run_buildquery.ts"


@functools.lru_cache(maxsize=1)
def runner_output() -> dict:
    """Invoke the TS runner once and cache its parsed JSON output."""
    proc = subprocess.run(
        ["tsx", str(RUNNER)],
        cwd=str(HARNESS),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"Harness failed (rc={proc.returncode}):\n"
        f"--- stdout ---\n{proc.stdout[-2000:]}\n"
        f"--- stderr ---\n{proc.stderr[-2000:]}"
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Harness produced non-JSON output:\n{proc.stdout[-2000:]}\n"
            f"stderr: {proc.stderr[-2000:]}"
        ) from exc


# ---------- f2p (fail at base, pass at gold) ----------


def test_no_sort_omits_orderby():
    """When neither sort_by_metric nor sort_by_series is enabled, the query must
    NOT include any orderby clause — even when 'series' is set. Adding a
    series sort unconditionally forces a multi-column ORDER BY, which on Druid
    prevents the native TopN optimization.
    """
    out = runner_output()
    case = out["no_sort"]
    assert case["orderby"] is None, (
        f"Expected no orderby when both sort flags are false, "
        f"got {case['orderby']!r}"
    )


def test_metric_only_orderby():
    """With sort_by_metric=true and sort_by_series=false, orderby must contain
    ONLY the metric sort — no implicit secondary series tiebreaker. The
    secondary series sort is what defeats Druid's TopN optimization.
    """
    out = runner_output()
    case = out["metric_only"]
    assert case["orderby"] == [["count", False]], (
        f"Expected orderby == [['count', False]] (metric DESC only), "
        f"got {case['orderby']!r}"
    )


def test_metric_only_orderby_high_cardinality():
    """Same contract under different metric/series/row_limit values, to guard
    against fixes that hardcode 'count' or 'foo'.
    """
    out = runner_output()
    case = out["high_cardinality_metric"]
    assert case["orderby"] == [["sum_population", False]], (
        f"Expected orderby == [['sum_population', False]], "
        f"got {case['orderby']!r}"
    )


# ---------- p2p (pass at base AND gold) ----------


def test_series_only_orderby():
    """With sort_by_series=true, orderby must include the series ASC sort."""
    out = runner_output()
    case = out["series_only"]
    assert case["orderby"] == [["foo", True]], (
        f"Expected orderby == [['foo', True]] (series ASC only), "
        f"got {case['orderby']!r}"
    )


def test_both_sorts_orderby():
    """With both sort flags enabled, orderby must contain metric DESC then
    series ASC, in that order.
    """
    out = runner_output()
    case = out["both_sorts"]
    assert case["orderby"] == [["count", False], ["foo", True]], (
        f"Expected orderby == [['count', False], ['foo', True]], "
        f"got {case['orderby']!r}"
    )


def test_existing_columns_check():
    """Pre-existing test contract: query.columns must come from formData.series.
    This must continue to pass — the fix should not regress it.
    """
    out = runner_output()
    case = out["columns_check"]
    assert case["columns"] == ["foo"], (
        f"Expected columns == ['foo'], got {case['columns']!r}"
    )
