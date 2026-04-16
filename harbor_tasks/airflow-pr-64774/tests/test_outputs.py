#!/usr/bin/env python3
"""
Tests for apache/airflow#64774: Allow newer packages when testing RC versions

This PR modifies the installation script to add --exclude-newer flag when
installing pre-release versions, allowing RC testing despite cooldown periods.
"""
import os
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/airflow")
SCRIPTS_PATH = REPO / "scripts" / "in_container"
sys.path.insert(0, str(SCRIPTS_PATH))


@pytest.fixture
def mock_in_container_utils():
    mock_module = MagicMock()
    mock_module.AIRFLOW_CORE_SOURCES_PATH = REPO / "airflow-core" / "src"
    mock_module.AIRFLOW_DIST_PATH = REPO / "dist"
    mock_module.AIRFLOW_ROOT_PATH = REPO
    mock_module.click = MagicMock()
    mock_module.console = MagicMock()
    mock_module.run_command = MagicMock(return_value=MagicMock(returncode=0))

    with patch.dict(sys.modules, {"in_container_utils": mock_module}):
        if "install_airflow_and_providers" in sys.modules:
            del sys.modules["install_airflow_and_providers"]
        yield mock_module


def test_prerelease_adds_exclude_newer_to_providers_install(mock_in_container_utils):
    """Test that providers install uses --exclude-newer when pre_release=True."""
    import install_airflow_and_providers as iap

    spec = iap.InstallationSpec(
        airflow_distribution="apache-airflow==3.2.0rc2",
        airflow_core_distribution=None,
        airflow_constraints_location=None,
        airflow_task_sdk_distribution=None,
        airflow_ctl_distribution=None,
        airflow_ctl_constraints_location=None,
        compile_ui_assets=False,
        mount_ui_dist=False,
        provider_distributions=["apache-airflow-providers-amazon"],
        provider_constraints_location=None,
        pre_release=True,
    )

    captured = []
    def capture(cmd, **kwargs):
        captured.append(cmd)
        return MagicMock(returncode=0)
    mock_in_container_utils.run_command.side_effect = capture

    iap._install_airflow_and_optionally_providers_together(spec, github_actions=False)

    assert len(captured) > 0, "No commands captured"
    cmd = captured[0]
    assert "--pre" in cmd, "Expected --pre flag"
    assert "--exclude-newer" in cmd, "Expected --exclude-newer flag for pre-release"

    idx = cmd.index("--exclude-newer")
    assert idx + 1 < len(cmd), "--exclude-newer must be followed by a timestamp"
    ts = cmd[idx + 1]
    iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    assert re.match(iso_pattern, ts), f"Expected ISO timestamp, got: {ts}"


def test_prerelease_adds_exclude_newer_to_airflow_install(mock_in_container_utils):
    """Test that airflow core install uses --exclude-newer when pre_release=True."""
    import install_airflow_and_providers as iap

    spec = iap.InstallationSpec(
        airflow_distribution="apache-airflow==3.2.0rc2",
        airflow_core_distribution=None,
        airflow_constraints_location=None,
        airflow_task_sdk_distribution=None,
        airflow_ctl_distribution=None,
        airflow_ctl_constraints_location=None,
        compile_ui_assets=False,
        mount_ui_dist=False,
        provider_distributions=[],
        provider_constraints_location=None,
        pre_release=True,
    )

    captured = []
    def capture(cmd, **kwargs):
        captured.append(cmd)
        return MagicMock(returncode=0)
    mock_in_container_utils.run_command.side_effect = capture

    iap._install_only_airflow_airflow_core_task_sdk_with_constraints(spec, github_actions=False)

    assert len(captured) > 0, "No commands captured"
    cmd = captured[0]
    assert "--pre" in cmd, "Expected --pre flag"
    assert "--exclude-newer" in cmd, "Expected --exclude-newer flag for pre-release"

    idx = cmd.index("--exclude-newer")
    assert idx + 1 < len(cmd), "--exclude-newer must be followed by a timestamp"
    ts = cmd[idx + 1]
    iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    assert re.match(iso_pattern, ts), f"Expected ISO timestamp, got: {ts}"


def test_no_prerelease_no_exclude_newer(mock_in_container_utils):
    """Test that --exclude-newer is NOT added when pre_release=False."""
    import install_airflow_and_providers as iap

    spec = iap.InstallationSpec(
        airflow_distribution="apache-airflow==3.1.0",
        airflow_core_distribution=None,
        airflow_constraints_location=None,
        airflow_task_sdk_distribution=None,
        airflow_ctl_distribution=None,
        airflow_ctl_constraints_location=None,
        compile_ui_assets=False,
        mount_ui_dist=False,
        provider_distributions=["apache-airflow-providers-amazon"],
        provider_constraints_location=None,
        pre_release=False,
    )

    captured = []
    def capture(cmd, **kwargs):
        captured.append(cmd)
        return MagicMock(returncode=0)
    mock_in_container_utils.run_command.side_effect = capture

    iap._install_airflow_and_optionally_providers_together(spec, github_actions=False)

    assert len(captured) > 0, "No commands captured"
    cmd = captured[0]
    assert "--pre" not in cmd, "--pre should not be in command when pre_release=False"
    assert "--exclude-newer" not in cmd, "--exclude-newer should not be in command when pre_release=False"


def test_datetime_functionality_available(mock_in_container_utils):
    """Test that datetime.now().isoformat() works in pre_release path."""
    import install_airflow_and_providers as iap

    spec = iap.InstallationSpec(
        airflow_distribution="apache-airflow==3.2.0rc2",
        airflow_core_distribution=None,
        airflow_constraints_location=None,
        airflow_task_sdk_distribution=None,
        airflow_ctl_distribution=None,
        airflow_ctl_constraints_location=None,
        compile_ui_assets=False,
        mount_ui_dist=False,
        provider_distributions=[],
        provider_constraints_location=None,
        pre_release=True,
    )

    captured = []
    def capture(cmd, **kwargs):
        captured.append(cmd)
        return MagicMock(returncode=0)
    mock_in_container_utils.run_command.side_effect = capture

    # Will raise NameError if datetime is not imported
    iap._install_only_airflow_airflow_core_task_sdk_with_constraints(spec, github_actions=False)

    assert len(captured) > 0, "No commands captured - datetime may not be available"
    cmd = captured[0]
    idx = cmd.index("--exclude-newer")
    ts = cmd[idx + 1]
    iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    assert re.match(iso_pattern, ts), f"Expected ISO timestamp, got: {ts}"


def test_prerelease_message_updated(mock_in_container_utils):
    """Test console message mentions both airflow and providers."""
    import install_airflow_and_providers as iap

    spec = iap.InstallationSpec(
        airflow_distribution="apache-airflow==3.2.0rc2",
        airflow_core_distribution=None,
        airflow_constraints_location=None,
        airflow_task_sdk_distribution=None,
        airflow_ctl_distribution=None,
        airflow_ctl_constraints_location=None,
        compile_ui_assets=False,
        mount_ui_dist=False,
        provider_distributions=[],
        provider_constraints_location=None,
        pre_release=True,
    )

    mock_in_container_utils.run_command.return_value = MagicMock(returncode=0)
    iap._install_only_airflow_airflow_core_task_sdk_with_constraints(spec, github_actions=False)

    print_calls = [str(c) for c in mock_in_container_utils.console.print.call_args_list]
    found = any("airflow and providers" in c for c in print_calls)
    assert found, f"Expected message to mention 'airflow and providers', got: {print_calls[:5]}"


import subprocess


def test_repo_ruff_lint():
    """Repo ruff linter passes on target file."""
    subprocess.run(["pip", "install", "--quiet", "ruff"], capture_output=True, timeout=120)
    r = subprocess.run(
        ["ruff", "check", "--force-exclude",
         str(REPO / "scripts" / "in_container" / "install_airflow_and_providers.py")],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo ruff formatter passes on target file."""
    subprocess.run(["pip", "install", "--quiet", "ruff"], capture_output=True, timeout=120)
    r = subprocess.run(
        ["ruff", "format", "--check",
         str(REPO / "scripts" / "in_container" / "install_airflow_and_providers.py")],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_in_container_dir_lint():
    """Repo ruff linter passes on entire in_container directory."""
    subprocess.run(["pip", "install", "--quiet", "ruff"], capture_output=True, timeout=120)
    r = subprocess.run(
        ["ruff", "check", "--force-exclude",
         str(REPO / "scripts" / "in_container")],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Ruff lint on in_container dir failed:\n{r.stdout}\n{r.stderr}"


def test_script_syntax_valid():
    """Script has valid Python syntax."""
    target_file = SCRIPTS_PATH / "install_airflow_and_providers.py"
    content = target_file.read_text()
    try:
        compile(content, str(target_file), "exec")
    except SyntaxError as e:
        pytest.fail(f"Script has invalid syntax: {e}")
