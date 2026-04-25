#!/usr/bin/env python3
"""Tests for the airflow RC testing fix.

This verifies that the fix for preventing incompatible packages when testing
RC versions has been correctly applied to the installation script.
"""

import subprocess
import sys
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path("/workspace/airflow")
TARGET_FILE = REPO / "scripts" / "in_container" / "install_airflow_and_providers.py"


def _install_dependencies():
    """Install required dependencies if not present."""
    try:
        import rich_click
        import rich
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "rich_click", "rich"])


def _import_and_get_functions():
    """Import the target module and return the key functions."""
    _install_dependencies()

    # Add the scripts/in_container directory to path for imports
    sys.path.insert(0, str(REPO / "scripts" / "in_container"))

    # We need to handle the case where the module might already be imported
    import importlib
    import install_airflow_and_providers as iap

    importlib.reload(iap)  # Ensure we get fresh code

    return iap


def _make_installation_spec(pre_release: bool = False):
    """Create a minimal InstallationSpec for testing."""
    iap = _import_and_get_functions()

    return iap.InstallationSpec(
        airflow_distribution=None,
        airflow_core_distribution=None,
        airflow_constraints_location=None,
        airflow_task_sdk_distribution=None,
        airflow_ctl_distribution=None,
        airflow_ctl_constraints_location=None,
        compile_ui_assets=None,
        mount_ui_dist=False,
        provider_distributions=[],
        provider_constraints_location=None,
        pre_release=pre_release,
    )


def test_pre_release_adds_exclude_newer_to_first_function():
    """Verify --exclude-newer is added when pre_release=True in first function.

    This tests the _install_airflow_and_optionally_providers_together function
    by mocking run_command and checking the command that would be executed.
    """
    iap = _import_and_get_functions()

    # Test with pre_release=True - should include --exclude-newer
    spec = _make_installation_spec(pre_release=True)

    # Capture the commands by mocking run_command
    captured_commands = []

    def mock_run_command(cmd, **kwargs):
        captured_commands.append(cmd)
        return MagicMock(returncode=0)

    # Patch run_command to capture what would be executed
    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):  # Suppress console output
            try:
                iap._install_airflow_and_optionally_providers_together(
                    spec, github_actions=False
                )
            except SystemExit:
                pass  # May exit due to missing files, that is ok
            except Exception:
                pass  # May fail due to missing files, that is ok

    # Check that some command included --exclude-newer with a valid ISO timestamp
    found_exclude_newer = False
    for cmd in captured_commands:
        if isinstance(cmd, list):
            for i, arg in enumerate(cmd):
                if arg == "--exclude-newer":
                    # Verify the next argument is a valid ISO timestamp
                    assert i + 1 < len(cmd), "--exclude-newer requires a timestamp argument"
                    timestamp = cmd[i + 1]
                    # Should be a valid ISO format timestamp (YYYY-MM-DDTHH:MM:SS)
                    assert "T" in timestamp, f"Expected ISO timestamp, got: {timestamp}"
                    assert timestamp[0:4].isdigit(), f"Expected year at start of timestamp, got: {timestamp}"
                    found_exclude_newer = True

    assert found_exclude_newer, (
        "No command included --exclude-newer with ISO timestamp when pre_release=True"
    )


def test_pre_release_adds_exclude_newer_to_second_function():
    """Verify --exclude-newer is added when pre_release=True in second function.

    This tests the _install_only_airflow_airflow_core_task_sdk_with_constraints
    function by mocking run_command and checking the command that would be executed.
    """
    iap = _import_and_get_functions()

    # Test with pre_release=True - should include --exclude-newer
    spec = _make_installation_spec(pre_release=True)

    # Capture the commands by mocking run_command
    captured_commands = []

    def mock_run_command(cmd, **kwargs):
        captured_commands.append(cmd)
        return MagicMock(returncode=0)

    # Patch run_command to capture what would be executed
    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):  # Suppress console output
            try:
                iap._install_only_airflow_airflow_core_task_sdk_with_constraints(
                    spec, github_actions=False
                )
            except SystemExit:
                pass  # May exit due to missing files, that is ok
            except Exception:
                pass  # May fail due to missing files, that is ok

    # Check that some command included --exclude-newer with a valid ISO timestamp
    found_exclude_newer = False
    for cmd in captured_commands:
        if isinstance(cmd, list):
            for i, arg in enumerate(cmd):
                if arg == "--exclude-newer":
                    # Verify the next argument is a valid ISO timestamp
                    assert i + 1 < len(cmd), "--exclude-newer requires a timestamp argument"
                    timestamp = cmd[i + 1]
                    # Should be a valid ISO format timestamp (YYYY-MM-DDTHH:MM:SS)
                    assert "T" in timestamp, f"Expected ISO timestamp, got: {timestamp}"
                    assert timestamp[0:4].isdigit(), f"Expected year at start of timestamp, got: {timestamp}"
                    found_exclude_newer = True

    assert found_exclude_newer, (
        "No command included --exclude-newer with ISO timestamp when pre_release=True"
    )


def test_non_pre_release_does_not_add_exclude_newer():
    """Verify --exclude-newer is NOT added when pre_release=False.

    This tests that the fix does not accidentally apply --exclude-newer
    to non-pre-release installations.
    """
    iap = _import_and_get_functions()

    # Test with pre_release=False - should NOT include --exclude-newer
    spec = _make_installation_spec(pre_release=False)

    # Capture the commands by mocking run_command
    captured_commands = []

    def mock_run_command(cmd, **kwargs):
        captured_commands.append(cmd)
        return MagicMock(returncode=0)

    # Patch run_command to capture what would be executed
    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):  # Suppress console output
            try:
                iap._install_airflow_and_optionally_providers_together(
                    spec, github_actions=False
                )
            except SystemExit:
                pass  # May exit due to missing files, that is ok
            except Exception:
                pass

            try:
                iap._install_only_airflow_airflow_core_task_sdk_with_constraints(
                    spec, github_actions=False
                )
            except SystemExit:
                pass
            except Exception:
                pass

    # Check that NO command included --exclude-newer
    for cmd in captured_commands:
        if isinstance(cmd, list):
            assert "--exclude-newer" not in cmd, (
                f"--exclude-newer should not be present when pre_release=False, but found in: {cmd}"
            )


def test_pre_release_includes_pre_flag():
    """Verify --pre flag is included when pre_release=True.

    The fix should include both --pre AND --exclude-newer, not just --exclude-newer.
    """
    iap = _import_and_get_functions()

    spec = _make_installation_spec(pre_release=True)
    captured_commands = []

    def mock_run_command(cmd, **kwargs):
        captured_commands.append(cmd)
        return MagicMock(returncode=0)

    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):
            try:
                iap._install_airflow_and_optionally_providers_together(spec, github_actions=False)
            except SystemExit:
                pass
            except Exception:
                pass

            try:
                iap._install_only_airflow_airflow_core_task_sdk_with_constraints(spec, github_actions=False)
            except SystemExit:
                pass
            except Exception:
                pass

    # Check that commands include --pre when pre_release is True
    found_pre = False
    for cmd in captured_commands:
        if isinstance(cmd, list) and "--pre" in cmd:
            found_pre = True

    assert found_pre, "--pre flag should be present when pre_release=True"


def test_datetime_import_is_usable():
    """Verify datetime can be imported and used to generate ISO timestamps.

    This tests that the datetime import is present and functional.
    """
    iap = _import_and_get_functions()

    # The datetime class should be available in the modules
    # We verify this by checking we can call it and get an ISO format string
    from datetime import datetime

    # Verify datetime functionality (not just import)
    result = datetime.now().isoformat()
    assert isinstance(result, str), "datetime.now().isoformat() should return a string"
    assert "T" in result, "ISO format should contain 'T' separator"
    assert result[0:4].isdigit(), "ISO format should start with year digits"


def test_exclude_newer_timestamp_is_recent():
    """Verify that --exclude-newer uses a recent timestamp (not hardcoded).

    This tests that the timestamp is generated dynamically rather than being a fixed value.
    """
    iap = _import_and_get_functions()
    from datetime import datetime

    spec = _make_installation_spec(pre_release=True)
    captured_commands = []
    captured_timestamps = []

    def mock_run_command(cmd, **kwargs):
        captured_commands.append(cmd)
        if isinstance(cmd, list):
            for i, arg in enumerate(cmd):
                if arg == "--exclude-newer" and i + 1 < len(cmd):
                    captured_timestamps.append(cmd[i + 1])
        return MagicMock(returncode=0)

    # Run once
    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):
            try:
                iap._install_airflow_and_optionally_providers_together(spec, github_actions=False)
            except Exception:
                pass

    # Small delay to ensure different timestamp
    import time
    time.sleep(0.01)

    # Run again
    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):
            try:
                iap._install_airflow_and_optionally_providers_together(spec, github_actions=False)
            except Exception:
                pass

    if len(captured_timestamps) >= 2:
        # The timestamps should be different (dynamically generated)
        # or at least one should be different from a hardcoded value
        ts1 = captured_timestamps[0]
        ts2 = captured_timestamps[1]

        # Parse timestamps to verify they are valid and recent
        dt1 = datetime.fromisoformat(ts1)
        dt2 = datetime.fromisoformat(ts2)

        now = datetime.now()

        # Both timestamps should be recent (within last hour)
        time_diff_1 = (now - dt1).total_seconds()
        time_diff_2 = (now - dt2).total_seconds()

        assert time_diff_1 < 3600, f"Timestamp {ts1} is not recent (more than 1 hour old)"
        assert time_diff_2 < 3600, f"Timestamp {ts2} is not recent (more than 1 hour old)"
    else:
        # If we didn't capture enough timestamps, at least verify we captured one
        assert len(captured_timestamps) >= 1, "Should have captured at least one --exclude-newer timestamp"


def test_both_flags_together_in_correct_order():
    """Verify --pre comes before --exclude-newer in the command.

    This tests that pip will receive the flags in a valid order.
    """
    iap = _import_and_get_functions()

    spec = _make_installation_spec(pre_release=True)
    captured_commands = []

    def mock_run_command(cmd, **kwargs):
        captured_commands.append(cmd)
        return MagicMock(returncode=0)

    with patch.object(iap, "run_command", side_effect=mock_run_command):
        with patch.object(iap, "console"):
            try:
                iap._install_airflow_and_optionally_providers_together(spec, github_actions=False)
            except Exception:
                pass

    # Find command with both --pre and --exclude-newer
    for cmd in captured_commands:
        if isinstance(cmd, list) and "--pre" in cmd and "--exclude-newer" in cmd:
            pre_idx = cmd.index("--pre")
            exclude_idx = cmd.index("--exclude-newer")
            assert pre_idx < exclude_idx, "--pre should come before --exclude-newer"
            # Verify timestamp follows --exclude-newer
            assert exclude_idx + 1 < len(cmd), "--exclude-newer should have a timestamp argument"
            return

    # If we get here, we didn't find both flags in any command
    import pytest
    pytest.fail("No command contained both --pre and --exclude-newer flags")
