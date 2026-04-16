"""Test outputs for dagster-default-partitions-validation task.

Tests validation of DefaultPartitionsSubset compatibility with TimeWindowPartitionsDefinition.
"""

import subprocess
import sys
import dagster as dg
from dagster._core.asset_graph_view.serializable_entity_subset import SerializableEntitySubset
from dagster._core.definitions.partitions.subset import DefaultPartitionsSubset

REPO = "/workspace/dagster"


def test_default_subset_with_invalid_keys():
    """DefaultPartitionsSubset with non-time keys should NOT be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    invalid_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"foo", "bar"}),
    )
    result = invalid_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, f"Expected False for invalid keys, got {result}"


def test_default_subset_with_valid_keys():
    """DefaultPartitionsSubset with valid time keys should be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    valid_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01", "2024-01-02"}),
    )
    result = valid_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is True, f"Expected True for valid keys, got {result}"


def test_default_subset_with_mixed_keys():
    """DefaultPartitionsSubset with mixed keys (some valid, some invalid) should NOT be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    mixed_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01", "invalid_key"}),
    )
    result = mixed_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, f"Expected False for mixed keys, got {result}"


def test_default_subset_with_out_of_range_keys():
    """DefaultPartitionsSubset with keys outside the partition range should NOT be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    out_of_range_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2020-01-01"}),  # before start_date
    )
    result = out_of_range_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, f"Expected False for out-of-range keys, got {result}"


def test_various_time_formats():
    """Test various time window partitions definitions with valid/invalid keys."""
    # Hourly partitions
    hourly_def = dg.HourlyPartitionsDefinition(start_date="2024-01-01-00:00")
    a = dg.AssetKey("a")

    hourly_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01-00:00", "2024-01-01-01:00"}),
    )
    result = hourly_subset.is_compatible_with_partitions_def(hourly_def)
    assert result is True, f"Expected True for valid hourly keys, got {result}"

    # Monthly partitions
    monthly_def = dg.MonthlyPartitionsDefinition(start_date="2024-01-01")
    monthly_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01", "2024-02-01"}),
    )
    result = monthly_subset.is_compatible_with_partitions_def(monthly_def)
    assert result is True, f"Expected True for valid monthly keys, got {result}"


def test_empty_subset():
    """Empty DefaultPartitionsSubset should be compatible with any time window partitions def."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    empty_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset(set()),
    )
    result = empty_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is True, f"Expected True for empty subset (all() returns True on empty), got {result}"


def test_repo_ruff():
    """Repo's ruff linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["make", "ruff"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Ruff failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_repo_ruff_check():
    """Repo's ruff check passes (pass_to_pass)."""
    r = subprocess.run(
        ["make", "check_ruff"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_partitions_subset():
    """Partition subset tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/dagster/dagster_tests/asset_defs_tests/test_partitions_subset.py",
            "-v", "-x"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Partitions subset tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_core_partition():
    """Core partition tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/dagster/dagster_tests/core_tests/partition_tests/test_partition.py",
            "-v", "-x"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Core partition tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_upstream_tests():
    """Run the upstream tests for serializable_entity_subset to ensure no regressions."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/dagster/dagster_tests/core_tests/asset_graph_view_tests/test_serializable_entity_subset.py",
            "-v", "-x"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Upstream tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"
