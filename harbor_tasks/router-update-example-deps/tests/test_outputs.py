"""Tests for the update-example-deps.mjs script."""

import json
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

REPO = "/workspace/router"


def test_script_file_exists():
    """The update-example-deps.mjs script file exists."""
    script_path = Path(REPO) / "scripts" / "update-example-deps.mjs"
    assert script_path.exists(), f"Script not found at {script_path}"
    assert script_path.is_file(), f"{script_path} is not a file"


def test_script_is_valid_javascript():
    """The script is syntactically valid JavaScript/Node.js."""
    script_path = Path(REPO) / "scripts" / "update-example-deps.mjs"
    if not script_path.exists():
        raise AssertionError("Script does not exist - skipping syntax check")

    # Check syntax with node --check
    result = subprocess.run(
        ["node", "--check", str(script_path)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Script has syntax errors:\n{result.stderr}"


def test_changeset_version_script_updated():
    """package.json changeset:version script calls update-example-deps.mjs."""
    package_json_path = Path(REPO) / "package.json"
    with open(package_json_path) as f:
        pkg = json.load(f)

    changeset_version = pkg.get("scripts", {}).get("changeset:version", "")
    assert "update-example-deps.mjs" in changeset_version, \
        f"changeset:version script does not call update-example-deps.mjs: {changeset_version}"


def test_script_updates_example_dependencies():
    """Running the script updates workspace dependencies in examples."""
    script_path = Path(REPO) / "scripts" / "update-example-deps.mjs"
    if not script_path.exists():
        raise AssertionError("Script does not exist - cannot test functionality")

    # Create a temporary test environment
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Copy the repo structure we need
        packages_dir = tmpdir / "packages"
        examples_dir = tmpdir / "examples"
        packages_dir.mkdir()
        examples_dir.mkdir()

        # Create a fake workspace package with version
        fake_pkg_dir = packages_dir / "fake-workspace-pkg"
        fake_pkg_dir.mkdir()
        (fake_pkg_dir / "package.json").write_text(json.dumps({
            "name": "@tanstack/fake-workspace-pkg",
            "version": "1.2.3"
        }))

        # Create another fake package
        fake_pkg_dir2 = packages_dir / "another-pkg"
        fake_pkg_dir2.mkdir()
        (fake_pkg_dir2 / "package.json").write_text(json.dumps({
            "name": "@tanstack/another-pkg",
            "version": "4.5.6"
        }))

        # Create an example with outdated dependencies
        example_dir = examples_dir / "test-example"
        example_dir.mkdir()
        original_deps = {
            "name": "test-example",
            "dependencies": {
                "@tanstack/fake-workspace-pkg": "^1.0.0",  # outdated
                "@tanstack/another-pkg": "^4.0.0",  # outdated
                "some-external-dep": "^2.0.0"  # not a workspace dep, should be unchanged
            },
            "devDependencies": {
                "@tanstack/fake-workspace-pkg": "^1.1.0"  # outdated dev dep
            }
        }
        (example_dir / "package.json").write_text(json.dumps(original_deps, indent=2))

        # Copy and modify the script to use our temp directory
        script_content = script_path.read_text()
        # Replace the rootDir calculation with our temp directory
        modified_script = script_content.replace(
            "path.join(import.meta.dirname, '..')",
            f"'{tmpdir}'"
        )

        modified_script_path = tmpdir / "update-example-deps.mjs"
        modified_script_path.write_text(modified_script)

        # Run the modified script
        result = subprocess.run(
            ["node", str(modified_script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check the script ran successfully
        assert result.returncode == 0, f"Script failed:\n{result.stderr}"

        # Read the updated example package.json
        updated_content = json.loads((example_dir / "package.json").read_text())

        # Verify workspace dependencies were updated
        assert updated_content["dependencies"]["@tanstack/fake-workspace-pkg"] == "^1.2.3", \
            "Workspace dependency not updated to correct version"
        assert updated_content["dependencies"]["@tanstack/another-pkg"] == "^4.5.6", \
            "Second workspace dependency not updated"

        # Verify external dependency was NOT changed
        assert updated_content["dependencies"]["some-external-dep"] == "^2.0.0", \
            "External dependency was incorrectly modified"

        # Verify devDependencies were updated
        assert updated_content["devDependencies"]["@tanstack/fake-workspace-pkg"] == "^1.2.3", \
            "Dev dependency not updated"

        # Verify the script reported updates
        assert "Updated" in result.stdout, "Script did not report updates"


def test_script_preserves_json_formatting():
    """The script preserves JSON formatting with 2-space indentation."""
    script_path = Path(REPO) / "scripts" / "update-example-deps.mjs"
    if not script_path.exists():
        raise AssertionError("Script does not exist - cannot test formatting")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Setup minimal structure
        packages_dir = tmpdir / "packages"
        examples_dir = tmpdir / "examples"
        packages_dir.mkdir()
        examples_dir.mkdir()

        fake_pkg_dir = packages_dir / "test-pkg"
        fake_pkg_dir.mkdir()
        (fake_pkg_dir / "package.json").write_text(json.dumps({
            "name": "@tanstack/test-pkg",
            "version": "2.0.0"
        }))

        example_dir = examples_dir / "test"
        example_dir.mkdir()
        # Write with specific formatting
        original_json = '{\n  "name": "test",\n  "dependencies": {\n    "@tanstack/test-pkg": "^1.0.0"\n  }\n}\n'
        (example_dir / "package.json").write_text(original_json)

        # Modify and run script
        script_content = script_path.read_text()
        modified_script = script_content.replace(
            "path.join(import.meta.dirname, '..')",
            f"'{tmpdir}'"
        )
        modified_script_path = tmpdir / "update-example-deps.mjs"
        modified_script_path.write_text(modified_script)

        result = subprocess.run(
            ["node", str(modified_script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0

        # Read result and verify formatting
        result_content = (example_dir / "package.json").read_text()
        # Should have 2-space indentation and trailing newline
        assert "  \"name\":" in result_content, "JSON formatting not preserved (indentation)"
        assert result_content.endswith("\n"), "Trailing newline not preserved"


def test_script_excludes_node_modules():
    """The script excludes node_modules from glob search."""
    script_path = Path(REPO) / "scripts" / "update-example-deps.mjs"
    if not script_path.exists():
        raise AssertionError("Script does not exist - cannot test exclusion")

    # Read script and verify node_modules exclusion
    script_content = script_path.read_text()
    assert "node_modules" in script_content, \
        "Script should exclude node_modules from search"
    assert "exclude" in script_content, \
        "Script should use exclude option in globSync"


def test_repo_package_json_valid():
    """The repo's package.json is valid JSON."""
    package_json_path = Path(REPO) / "package.json"
    with open(package_json_path) as f:
        pkg = json.load(f)
    assert "scripts" in pkg, "package.json missing scripts section"


def test_repo_lint():
    """Repo's linter passes on core package (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "nx", "run-many", "--target=test:eslint", "--projects=@tanstack/react-router"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_types():
    """TypeScript typecheck passes on core package (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "nx", "run-many", "--target=test:types", "--projects=@tanstack/react-router"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-500:]}"


def test_repo_unit_tests():
    """Unit tests pass on core package (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "nx", "run-many", "--target=test:unit", "--projects=@tanstack/react-router"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"


def test_repo_build():
    """Build succeeds on core package (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "nx", "run-many", "--target=build", "--projects=@tanstack/react-router"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-500:]}"


def test_repo_docs_links():
    """Documentation links are valid (pass_to_pass)."""
    result = subprocess.run(
        ["node", "--experimental-strip-types", "scripts/verify-links.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Docs link check failed:\n{result.stderr[-500:]}"


def test_repo_format():
    """Repo formatting follows prettier standards (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--experimental-cli", "--check", "package.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Format check failed:\n{result.stderr[-500:]}"
