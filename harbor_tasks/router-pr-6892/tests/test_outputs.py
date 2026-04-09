"""Tests for the update-example-deps script task.

This validates that the fix correctly:
1. Adds the update-example-deps.mjs script
2. Updates package.json to call the script during changeset:version
3. The script correctly updates example dependencies to match workspace versions
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/router")
SCRIPT_PATH = REPO / "scripts" / "update-example-deps.mjs"
PACKAGE_JSON = REPO / "package.json"
PACKAGES_DIR = REPO / "packages"
EXAMPLES_DIR = REPO / "examples"


def test_script_file_exists():
    """F2P: Script file must exist at the correct path."""
    assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    assert SCRIPT_PATH.is_file(), f"{SCRIPT_PATH} is not a file"


def test_package_json_updated():
    """F2P: package.json must call the script in changeset:version."""
    with open(PACKAGE_JSON, "r") as f:
        pkg = json.load(f)

    changeset_version = pkg.get("scripts", {}).get("changeset:version", "")
    assert "node scripts/update-example-deps.mjs" in changeset_version, (
        f"changeset:version script does not call update-example-deps.mjs: {changeset_version}"
    )


def test_script_is_valid_javascript():
    """P2P: Script must be syntactically valid JavaScript."""
    if not SCRIPT_PATH.exists():
        pytest.skip("Script file does not exist")

    # Check syntax with node --check
    result = subprocess.run(
        ["node", "--check", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"


def test_script_updates_example_deps():
    """F2P: Script must correctly update example dependencies to match workspace versions.

    This test:
    1. Finds a workspace package and its version
    2. Creates/modifies an example to use an outdated version
    3. Runs the script
    4. Verifies the example was updated to the correct version
    """
    if not SCRIPT_PATH.exists():
        pytest.skip("Script file does not exist")

    # Find a workspace package with a version
    workspace_packages = {}
    for pkg_json in PACKAGES_DIR.glob("*/package.json"):
        with open(pkg_json, "r") as f:
            pkg = json.load(f)
            if "name" in pkg and "version" in pkg:
                workspace_packages[pkg["name"]] = pkg["version"]

    if not workspace_packages:
        pytest.skip("No workspace packages found")

    # Pick the first workspace package
    test_pkg_name, test_pkg_version = next(iter(workspace_packages.items()))

    # Create a minimal test example structure
    test_example_dir = EXAMPLES_DIR / "test-update-example"
    test_example_pkg = test_example_dir / "package.json"

    try:
        # Create test example with outdated version
        test_example_dir.mkdir(parents=True, exist_ok=True)
        outdated_version = "^0.0.1-old"  # Intentionally wrong version
        test_pkg = {
            "name": "test-update-example",
            "dependencies": {test_pkg_name: outdated_version},
        }
        with open(test_example_pkg, "w") as f:
            json.dump(test_pkg, f, indent=2)

        # Run the script
        result = subprocess.run(
            ["node", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO,
        )

        # Script should succeed
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Verify the example was updated
        with open(test_example_pkg, "r") as f:
            updated_pkg = json.load(f)

        expected_version = f"^{test_pkg_version}"
        actual_version = updated_pkg.get("dependencies", {}).get(test_pkg_name)

        assert actual_version == expected_version, (
            f"Version not updated correctly. Expected {expected_version}, got {actual_version}"
        )

    finally:
        # Cleanup
        import shutil
        if test_example_dir.exists():
            shutil.rmtree(test_example_dir)


def test_script_handles_no_changes():
    """P2P: Script should handle cases where no updates are needed.

    The script should complete successfully even when all versions are already correct.
    """
    if not SCRIPT_PATH.exists():
        pytest.skip("Script file does not exist")

    # Run the script - it should complete without error even if nothing to update
    result = subprocess.run(
        ["node", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Script failed when no changes needed: {result.stderr}"
    # Script should output the completion message
    assert "Done. Updated" in result.stdout, f"Expected completion message, got: {result.stdout}"


def test_script_skips_non_workspace_deps():
    """P2P: Script should not modify dependencies that aren't in the workspace.

    External packages (like 'react', 'lodash', etc.) should be left untouched.
    """
    if not SCRIPT_PATH.exists():
        pytest.skip("Script file does not exist")

    # Create a test example with external dependencies
    test_example_dir = EXAMPLES_DIR / "test-external-deps"
    test_example_pkg = test_example_dir / "package.json"

    try:
        test_example_dir.mkdir(parents=True, exist_ok=True)
        external_dep_version = "^18.2.0"
        test_pkg = {
            "name": "test-external-deps",
            "dependencies": {"react": external_dep_version, "non-existent-pkg": "^1.0.0"},
        }
        original_content = json.dumps(test_pkg, indent=2)
        with open(test_example_pkg, "w") as f:
            f.write(original_content)

        # Run the script
        result = subprocess.run(
            ["node", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Verify the example was NOT updated (no workspace packages in it)
        with open(test_example_pkg, "r") as f:
            updated_pkg = json.load(f)

        assert updated_pkg["dependencies"]["react"] == external_dep_version, (
            "External dependency was incorrectly modified"
        )

    finally:
        # Cleanup
        import shutil
        if test_example_dir.exists():
            shutil.rmtree(test_example_dir)


def test_script_updates_both_deps_and_devdeps():
    """P2P: Script should update both dependencies and devDependencies.

    The script should handle both dep types correctly.
    """
    if not SCRIPT_PATH.exists():
        pytest.skip("Script file does not exist")

    # Find a workspace package
    workspace_packages = {}
    for pkg_json in PACKAGES_DIR.glob("*/package.json"):
        with open(pkg_json, "r") as f:
            pkg = json.load(f)
            if "name" in pkg and "version" in pkg:
                workspace_packages[pkg["name"]] = pkg["version"]

    if not workspace_packages:
        pytest.skip("No workspace packages found")

    test_pkg_name, test_pkg_version = next(iter(workspace_packages.items()))

    # Create test example with devDependencies
    test_example_dir = EXAMPLES_DIR / "test-devdeps"
    test_example_pkg = test_example_dir / "package.json"

    try:
        test_example_dir.mkdir(parents=True, exist_ok=True)
        outdated_version = "^0.0.1-old"
        test_pkg = {
            "name": "test-devdeps",
            "devDependencies": {test_pkg_name: outdated_version},
        }
        with open(test_example_pkg, "w") as f:
            json.dump(test_pkg, f, indent=2)

        # Run the script
        result = subprocess.run(
            ["node", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=REPO,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Verify devDependencies were updated
        with open(test_example_pkg, "r") as f:
            updated_pkg = json.load(f)

        expected_version = f"^{test_pkg_version}"
        actual_version = updated_pkg.get("devDependencies", {}).get(test_pkg_name)

        assert actual_version == expected_version, (
            f"devDependencies not updated. Expected {expected_version}, got {actual_version}"
        )

    finally:
        # Cleanup
        import shutil
        if test_example_dir.exists():
            shutil.rmtree(test_example_dir)
