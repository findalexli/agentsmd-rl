"""Tests for the partition subset validation fix.

This tests that DefaultPartitionsSubset is properly validated against
TimeWindowPartitionsDefinition to ensure all keys are valid time window keys.
"""

import sys
import os

# Add the dagster package to the path
sys.path.insert(0, "/workspace/dagster/python_modules/dagster")

import dagster as dg
from dagster._core.asset_graph_view.serializable_entity_subset import SerializableEntitySubset
from dagster._core.definitions.partitions.subset import DefaultPartitionsSubset


def test_default_subset_with_non_time_keys_not_compatible():
    """DefaultPartitionsSubset with non-time keys should NOT be compatible with time window def."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    invalid_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"foo", "bar"}),
    )
    result = invalid_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, "Non-time keys should not be compatible with time window partitions"


def test_default_subset_with_valid_time_keys_compatible():
    """DefaultPartitionsSubset with valid time keys should be compatible with time window def."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    valid_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01", "2024-01-02"}),
    )
    result = valid_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is True, "Valid time keys should be compatible with time window partitions"


def test_default_subset_with_mixed_keys_not_compatible():
    """DefaultPartitionsSubset with mixed keys (some valid, some invalid) should NOT be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    mixed_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01", "invalid_key"}),
    )
    result = mixed_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, "Mixed valid/invalid keys should not be compatible with time window partitions"


def test_default_subset_with_out_of_range_keys_not_compatible():
    """DefaultPartitionsSubset with keys outside the partition range should NOT be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    out_of_range_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2020-01-01"}),  # before start_date
    )
    result = out_of_range_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, "Out-of-range keys should not be compatible with time window partitions"


def test_default_subset_with_single_invalid_key_not_compatible():
    """DefaultPartitionsSubset with a single invalid time-like key should NOT be compatible."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    invalid_time_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-13-45"}),  # invalid date
    )
    result = invalid_time_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is False, "Invalid time format should not be compatible with time window partitions"


def test_default_subset_compatibility_vary_partitions_defs():
    """Test compatibility with different time window partition definitions."""
    hourly_def = dg.HourlyPartitionsDefinition(start_date="2024-01-01-00:00")
    weekly_def = dg.WeeklyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    # Test hourly partitions with valid hourly keys
    hourly_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-01-00:00", "2024-01-01-01:00"}),
    )
    result = hourly_subset.is_compatible_with_partitions_def(hourly_def)
    assert result is True, "Valid hourly keys should be compatible with hourly partitions"

    # Test weekly partitions with valid weekly keys
    weekly_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset({"2024-01-07"}),
    )
    result = weekly_subset.is_compatible_with_partitions_def(weekly_def)
    assert result is True, "Valid weekly keys should be compatible with weekly partitions"

    # Test hourly keys against daily definition (should fail)
    daily_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    result = hourly_subset.is_compatible_with_partitions_def(daily_def)
    assert result is False, "Hourly keys should not be compatible with daily partitions"


def test_empty_default_subset_compatible():
    """Empty DefaultPartitionsSubset should be compatible with any partitions def."""
    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
    a = dg.AssetKey("a")

    empty_subset = SerializableEntitySubset(
        key=a,
        value=DefaultPartitionsSubset(set()),
    )
    result = empty_subset.is_compatible_with_partitions_def(time_window_partitions_def)
    assert result is True, "Empty subset should be compatible with any partitions definition"


# ---------------------------------------------------------------------------
# Pass-to-pass tests: repo's own CI tests that must continue to pass
# ---------------------------------------------------------------------------

import subprocess

REPO = "/workspace/dagster"


def test_repo_serializable_entity_subset():
    """Repo's test_serializable_entity_subset passes (pass_to_pass)."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/dagster/dagster_tests/core_tests/asset_graph_view_tests/test_serializable_entity_subset.py",
            "-v",
        ],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Repo serializable_entity_subset tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_partition_tests():
    """Repo's core partition tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/dagster/dagster_tests/core_tests/partition_tests/",
            "-v",
        ],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Repo partition tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_partitions_subset_tests():
    """Repo's partitions_subset tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "python_modules/dagster/dagster_tests/asset_defs_tests/test_partitions_subset.py",
            "-v",
        ],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Repo partitions_subset tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
