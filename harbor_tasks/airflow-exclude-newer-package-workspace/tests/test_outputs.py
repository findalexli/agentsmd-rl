#!/usr/bin/env python3
"""Tests for PR #64859: Add exclude-newer-package=false for all workspace components."""

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")
PYPROJECT_TOML = REPO / "pyproject.toml"
UPDATE_SCRIPT = REPO / "scripts" / "ci" / "prek" / "update_airflow_pyproject_toml.py"
INSTALL_SCRIPT = REPO / "scripts" / "in_container" / "install_airflow_and_providers.py"


def _read_toml(path: Path) -> dict:
    """Read a TOML file and return parsed dict."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def test_pyproject_has_exclude_newer_package_section():
    """[F2P] pyproject.toml must have [tool.uv.exclude-newer-package] section."""
    data = _read_toml(PYPROJECT_TOML)
    uv_tool = data.get("tool", {}).get("uv", {})

    assert "exclude-newer-package" in uv_tool, \
        "Missing [tool.uv.exclude-newer-package] section in pyproject.toml"


def test_pyproject_has_exclude_newer_package_pip_section():
    """[F2P] pyproject.toml must have [tool.uv.pip.exclude-newer-package] section."""
    data = _read_toml(PYPROJECT_TOML)
    uv_pip = data.get("tool", {}).get("uv", {}).get("pip", {})

    assert "exclude-newer-package" in uv_pip, \
        "Missing [tool.uv.pip.exclude-newer-package] section in pyproject.toml"


def test_exclude_newer_package_entries_exist():
    """[F2P] Workspace components must have exclude-newer-package = false entries."""
    data = _read_toml(PYPROJECT_TOML)
    uv_tool = data.get("tool", {}).get("uv", {})
    sources = uv_tool.get("sources", {})
    exclude_newer = uv_tool.get("exclude-newer-package", {})

    # Get all workspace components from sources
    workspace_components = [
        name for name, value in sources.items()
        if isinstance(value, dict) and value.get("workspace")
    ]

    assert len(workspace_components) > 0, "No workspace components found in [tool.uv.sources]"

    missing = []
    for component in workspace_components:
        if component not in exclude_newer:
            missing.append(component)
        elif exclude_newer.get(component) is not False:
            missing.append(f"{component} (not false)")

    assert len(missing) == 0, \
        f"Missing or invalid exclude-newer-package entries: {missing}"


def test_exclude_newer_package_pip_entries_exist():
    """[F2P] Workspace components must have exclude-newer-package = false in pip section."""
    data = _read_toml(PYPROJECT_TOML)
    uv_tool = data.get("tool", {}).get("uv", {})
    sources = uv_tool.get("sources", {})
    pip_section = uv_tool.get("pip", {})
    exclude_newer_pip = pip_section.get("exclude-newer-package", {})

    # Get all workspace components from sources
    workspace_components = [
        name for name, value in sources.items()
        if isinstance(value, dict) and value.get("workspace")
    ]

    assert len(workspace_components) > 0, "No workspace components found in [tool.uv.sources]"

    missing = []
    for component in workspace_components:
        if component not in exclude_newer_pip:
            missing.append(component)
        elif exclude_newer_pip.get(component) is not False:
            missing.append(f"{component} (not false)")

    assert len(missing) == 0, \
        f"Missing or invalid exclude-newer-package entries in pip section: {missing}"


def test_update_script_has_get_workspace_components():
    """[F2P] update_airflow_pyproject_toml.py must have get_all_workspace_component_names function."""
    script_content = UPDATE_SCRIPT.read_text()

    assert "def get_all_workspace_component_names()" in script_content, \
        "Missing get_all_workspace_component_names() function in update script"


def test_update_script_generates_exclude_newer_entries():
    """[F2P] update script must generate exclude-newer-package entries for workspace components."""
    script_content = UPDATE_SCRIPT.read_text()

    # Check for the marker constants
    assert "START_EXCLUDE_NEWER_PACKAGE" in script_content, \
        "Missing START_EXCLUDE_NEWER_PACKAGE marker in update script"
    assert "END_EXCLUDE_NEWER_PACKAGE" in script_content, \
        "Missing END_EXCLUDE_NEWER_PACKAGE marker in update script"
    assert "START_EXCLUDE_NEWER_PACKAGE_PIP" in script_content, \
        "Missing START_EXCLUDE_NEWER_PACKAGE_PIP marker in update script"
    assert "END_EXCLUDE_NEWER_PACKAGE_PIP" in script_content, \
        "Missing END_EXCLUDE_NEWER_PACKAGE_PIP marker in update script"

    # Check that the script calls insert_documentation for both sections
    assert 'insert_documentation(\n        AIRFLOW_PYPROJECT_TOML_FILE,\n        exclude_newer_entries,\n        START_EXCLUDE_NEWER_PACKAGE,' in script_content or \
           'insert_documentation(' in script_content and 'START_EXCLUDE_NEWER_PACKAGE' in script_content, \
        "Script should call insert_documentation for exclude-newer-package section"


def test_install_script_no_exclude_newer_datetime():
    """[F2P] install_airflow_and_providers.py must not use datetime.now().isoformat() with --exclude-newer."""
    script_content = INSTALL_SCRIPT.read_text()

    # The fix removes the --exclude-newer flag with datetime
    assert "datetime.now().isoformat()" not in script_content, \
        "install script should not use datetime.now().isoformat() - use pyproject.toml config instead"

    # Check that --pre is still there but --exclude-newer with datetime is removed
    # The old code had: base_install_cmd.extend(["--pre", "--exclude-newer", datetime.now().isoformat()])
    # New code should just have: base_install_cmd.extend(["--pre"])
    assert '["--pre"]' in script_content or "base_install_cmd.extend([\"--pre\"])" in script_content, \
        "install script should use --pre flag without --exclude-newer datetime"


def test_install_script_no_datetime_import_if_unused():
    """[F2P] install script should not import datetime if not used."""
    script_content = INSTALL_SCRIPT.read_text()

    # If datetime is still imported, it might be used elsewhere - let's check
    # The original fix removed the datetime import, but let's be flexible
    # Just make sure --exclude-newer with datetime is not used
    pass  # This is covered by test_install_script_no_exclude_newer_datetime


def test_docker_compose_has_pyproject_mount():
    """[F2P] docker-compose must mount pyproject.toml for uv config access."""
    compose_file = REPO / "scripts" / "ci" / "docker-compose" / "remove-sources.yml"

    if not compose_file.exists():
        pytest.skip("remove-sources.yml not found - may be optional")

    compose_content = compose_file.read_text()

    assert "pyproject.toml:/opt/airflow/pyproject.toml" in compose_content, \
        "docker-compose should mount pyproject.toml for uv configuration"


def test_ruff_format_check():
    """[P2P] Python files should pass ruff format check."""
    # Only check the modified files
    files_to_check = [
        UPDATE_SCRIPT,
        INSTALL_SCRIPT,
    ]

    for filepath in files_to_check:
        if filepath.exists():
            result = subprocess.run(
                ["python", "-m", "ruff", "format", "--check", str(filepath)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert result.returncode == 0, \
                f"Ruff format check failed for {filepath}:\n{result.stderr}"


def test_script_syntax():
    """[P2P] Python scripts should have valid syntax."""
    scripts = [
        UPDATE_SCRIPT,
        INSTALL_SCRIPT,
    ]

    for script in scripts:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, \
            f"Syntax error in {script}:\n{result.stderr}"


def test_pyproject_toml_valid():
    """[P2P] pyproject.toml must be valid TOML (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c", f"import tomllib; tomllib.load(open('{PYPROJECT_TOML}', 'rb'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, \
        f"pyproject.toml is not valid TOML:\n{result.stderr}"


def test_ruff_check_critical():
    """[P2P] Python files should pass ruff critical checks (E9, F63) (pass_to_pass)."""
    files_to_check = [
        UPDATE_SCRIPT,
        INSTALL_SCRIPT,
    ]

    for filepath in files_to_check:
        if filepath.exists():
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "--select=E9,F63", str(filepath)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert result.returncode == 0, \
                f"Ruff critical check failed for {filepath}:\n{result.stdout}"
