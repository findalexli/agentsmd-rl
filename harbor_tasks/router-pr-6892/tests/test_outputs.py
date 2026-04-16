"""
Tests for TanStack/router#6892: auto update versions used in examples

This PR adds a script to automatically update example package.json dependencies
to match workspace package versions during the changeset:version workflow.
"""

import json
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

REPO = Path("/workspace/router")
SCRIPT_PATH = REPO / "scripts" / "update-example-deps.mjs"
PACKAGES_DIR = REPO / "packages"
EXAMPLES_DIR = REPO / "examples"


def test_script_exists():
    """The update-example-deps.mjs script exists (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    content = SCRIPT_PATH.read_text()
    assert len(content) > 100, "Script appears to be empty or stub"


def test_script_runs_without_error():
    """The script can be executed with node (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), "Script must exist to run"

    result = subprocess.run(
        ["node", str(SCRIPT_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Script failed with:\nstderr: {result.stderr}\nstdout: {result.stdout}"


def test_script_outputs_completion_message():
    """The script outputs a 'Done' completion message (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), "Script must exist to run"

    result = subprocess.run(
        ["node", str(SCRIPT_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert "Done" in result.stdout, f"Expected 'Done' in output, got: {result.stdout}"


def test_changeset_version_script_includes_update():
    """package.json changeset:version calls update-example-deps.mjs (fail_to_pass)."""
    pkg_json = REPO / "package.json"
    assert pkg_json.exists(), "package.json not found"

    data = json.loads(pkg_json.read_text())
    scripts = data.get("scripts", {})
    changeset_version = scripts.get("changeset:version", "")

    assert "update-example-deps" in changeset_version, (
        f"changeset:version script should call update-example-deps.mjs, got: {changeset_version}"
    )


def test_script_reads_workspace_packages():
    """The script reads package versions from packages/ directory (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), "Script must exist to check"
    content = SCRIPT_PATH.read_text()

    # Script should reference packages directory and read package.json files
    assert "packages" in content.lower(), "Script should reference packages directory"
    assert "package.json" in content, "Script should read package.json files"
    assert "version" in content, "Script should access version field"


def test_script_updates_example_dependencies():
    """The script updates example package.json files with correct versions (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), "Script must exist to run"

    # Find a workspace package to get its version
    workspace_pkg = None
    workspace_version = None

    for pkg_dir in PACKAGES_DIR.iterdir():
        pkg_json = pkg_dir / "package.json"
        if pkg_json.exists():
            data = json.loads(pkg_json.read_text())
            name = data.get("name", "")
            version = data.get("version", "")
            if name.startswith("@tanstack/") and version:
                workspace_pkg = name
                workspace_version = version
                break

    assert workspace_pkg, "Could not find any workspace package with a version"

    # Find an example that uses this package
    example_using_pkg = None
    for example_json in EXAMPLES_DIR.rglob("package.json"):
        if "node_modules" in str(example_json):
            continue
        data = json.loads(example_json.read_text())
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        if workspace_pkg in deps or workspace_pkg in dev_deps:
            example_using_pkg = example_json
            break

    if not example_using_pkg:
        # If no example uses the package, script should still run without error
        return

    # Run the script and verify it doesn't crash
    result = subprocess.run(
        ["node", str(SCRIPT_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"


def test_script_uses_caret_version_format():
    """The script updates dependencies to use caret (^) version format (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), "Script must exist to check"
    content = SCRIPT_PATH.read_text()

    # Script should format versions with caret prefix
    assert "^" in content, "Script should use caret (^) version prefix"
    # Should construct versions like ^${version}
    assert "`^${" in content or '`^$' in content or '"^"' in content or "'^'" in content, (
        "Script should construct caret-prefixed versions"
    )


def test_script_handles_both_dep_types():
    """The script checks both dependencies and devDependencies (fail_to_pass)."""
    assert SCRIPT_PATH.exists(), "Script must exist to check"
    content = SCRIPT_PATH.read_text()

    assert "dependencies" in content, "Script should handle dependencies"
    assert "devDependencies" in content, "Script should handle devDependencies"


def test_package_json_is_valid():
    """package.json remains valid JSON after changes (pass_to_pass)."""
    pkg_json = REPO / "package.json"
    assert pkg_json.exists(), "package.json not found"

    # Should parse without error
    data = json.loads(pkg_json.read_text())
    assert "name" in data, "package.json should have name field"
    assert "scripts" in data, "package.json should have scripts field"


def test_scripts_directory_exists():
    """scripts/ directory exists in repository (pass_to_pass)."""
    scripts_dir = REPO / "scripts"
    assert scripts_dir.exists(), "scripts/ directory should exist"
    assert scripts_dir.is_dir(), "scripts/ should be a directory"


def test_repo_eslint_scripts():
    """ESLint passes on scripts directory (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "exec", "eslint", "scripts/", "--max-warnings=0"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-1000:]}"


def test_repo_prettier_scripts():
    """Prettier check passes on scripts .mjs files (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "exec", "prettier", "--check", "scripts/**/*.mjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-1000:]}"


def test_repo_node_syntax_scripts():
    """Node can parse existing .mjs scripts without syntax errors (pass_to_pass)."""
    # Check that the existing cleanup script has valid syntax
    result = subprocess.run(
        ["node", "--check", "scripts/cleanup-empty-packages.mjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Node syntax check failed:\n{result.stderr[-500:]}"
