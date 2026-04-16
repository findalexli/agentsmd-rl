"""Test outputs for lancedb dependency update task."""

import subprocess
import re

REPO = "/workspace/lancedb"


def test_cargo_toml_lance_version_updated():
    """Verify that Cargo.toml has updated lance dependency versions."""
    with open(f"{REPO}/Cargo.toml", "r") as f:
        content = f.read()

    # Check that old version is gone
    assert "3.0.0-beta.5" not in content, "Old lance version 3.0.0-beta.5 still present"

    # Check that new version is present for all lance dependencies
    lance_deps = [
        "lance", "lance-core", "lance-datagen", "lance-file", "lance-io",
        "lance-index", "lance-linalg", "lance-namespace", "lance-namespace-impls",
        "lance-table", "lance-testing", "lance-datafusion", "lance-encoding", "lance-arrow"
    ]

    for dep in lance_deps:
        pattern = rf'{re.escape(dep)}.*?=.*"=3\.1\.0-beta\.2"'
        assert re.search(pattern, content), f"{dep} version not updated to 3.1.0-beta.2"


def test_java_pom_version_updated():
    """Verify that java/pom.xml has updated lance-core version."""
    with open(f"{REPO}/java/pom.xml", "r") as f:
        content = f.read()

    # Check old version is gone
    assert "3.0.0-beta.5" not in content, "Old lance-core.version 3.0.0-beta.5 still present"

    # Check new version is present
    assert "3.1.0-beta.2" in content, "New lance-core.version 3.1.0-beta.2 not found"


def test_cargo_lock_lance_version_updated():
    """Verify that Cargo.lock reflects the updated lance versions."""
    with open(f"{REPO}/Cargo.lock", "r") as f:
        content = f.read()

    # Check that old git tag references are gone
    assert "v3.0.0-beta.5" not in content, "Old lance tag v3.0.0-beta.5 still in Cargo.lock"

    # Check that new version is present
    assert "v3.1.0-beta.2" in content, "New lance tag v3.1.0-beta.2 not in Cargo.lock"


def test_cargo_check_passes():
    """Verify that cargo check passes with the updated dependencies."""
    result = subprocess.run(
        ["cargo", "check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_cargo_clippy_passes():
    """Verify that cargo clippy passes (repo's linting standard)."""
    result = subprocess.run(
        ["cargo", "clippy", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo clippy failed:\n{result.stderr[-1000:]}"


def test_cargo_fmt_check_passes():
    """Verify that cargo fmt --check passes (repo's formatting standard)."""
    result = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo fmt check failed:\n{result.stderr[-500:]}"


def test_cargo_clippy_all_features_passes():
    """Verify that cargo clippy with all features passes (CI linting standard)."""
    result = subprocess.run(
        ["cargo", "clippy", "--all-features", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo clippy --all-features failed:\n{result.stderr[-1000:]}"


def test_ruff_lint_python_passes():
    """Verify that ruff lint check on Python code passes."""
    result = subprocess.run(
        ["ruff", "check", f"{REPO}/python"],
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"ruff lint check failed:\n{result.stderr[-500:]}"


def test_cargo_metadata_valid():
    """Verify that cargo metadata can be parsed (workspace structure is valid)."""
    result = subprocess.run(
        ["cargo", "metadata", "--format-version=1", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"cargo metadata failed:\n{result.stderr[-500:]}"
    # Verify output is valid JSON and contains expected package
    assert "lancedb" in result.stdout, "lancedb package not found in metadata"
