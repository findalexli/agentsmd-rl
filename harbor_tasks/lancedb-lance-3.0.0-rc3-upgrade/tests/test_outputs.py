#!/usr/bin/env python3
"""
Tests for lancedb-lance-3.0.0-rc3-upgrade benchmark task.

This task involves upgrading the Lance dependency and fixing breaking API changes
in error handling patterns. The key changes are:
1. Update Cargo.toml versions from rc.2 to rc.3
2. Change lance_core::Error::io() calls to remove Default::default() argument
3. Update lance_core::Error::IO and InvalidInput constructors to use new API
4. Simplify error propagation with ? operator in namespace.rs
"""

import subprocess
import sys
import os

REPO = "/workspace/lancedb"


def run_cargo_check(cwd=None, timeout=300):
    """Run cargo check and return the result."""
    if cwd is None:
        cwd = REPO
    return subprocess.run(
        ["cargo", "check", "--message-format=short"],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd
    )


def test_cargo_toml_version():
    """Check that Cargo.toml has updated Lance version to rc.3"""
    cargo_toml = os.path.join(REPO, "Cargo.toml")
    with open(cargo_toml, "r") as f:
        content = f.read()

    # Check that version is now rc.3, not rc.2
    assert "3.0.0-rc.3" in content, "Cargo.toml should use Lance version 3.0.0-rc.3"
    assert "3.0.0-rc.2" not in content, "Cargo.toml should not still reference 3.0.0-rc.2"


def test_cargo_lock_version():
    """Check that Cargo.lock has updated Lance version to rc.3"""
    cargo_lock = os.path.join(REPO, "Cargo.lock")
    with open(cargo_lock, "r") as f:
        content = f.read()

    # Check that version is now rc.3
    assert "3.0.0-rc.3" in content, "Cargo.lock should reference Lance version 3.0.0-rc.3"


def test_python_namespace_error_api():
    """Check that python/src/namespace.rs uses new error API without Default::default()"""
    namespace_rs = os.path.join(REPO, "python/src/namespace.rs")
    with open(namespace_rs, "r") as f:
        content = f.read()

    # The new API should use Error::io(format!(...)) without Default::default()
    # Check that Default::default() is not used in lance_core::Error context
    error_io_calls = content.count("lance_core::Error::io")
    default_calls = content.count("Default::default()")

    assert error_io_calls > 0, "Should have lance_core::Error::io calls"
    # In the new API, Default::default() should not appear in Error::io calls
    # But we need to check context - it should be absent from error constructions

    # More specific check: look for pattern that indicates old API
    # Old: lance_core::Error::io(..., Default::default())
    # New: lance_core::Error::io(format!(...))

    # If we see "Default::default()" near "lance_core::Error", it's likely the old API
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "lance_core::Error" in line and "Default::default()" in line:
            # Check if this is in a comment or actual code
            stripped = line.strip()
            if not stripped.startswith("//") and not stripped.startswith("*"):
                raise AssertionError(f"Found old error API pattern at line {i+1}: {line.strip()}")


def test_storage_options_error_api():
    """Check that python/src/storage_options.rs uses new error constructors"""
    storage_rs = os.path.join(REPO, "python/src/storage_options.rs")
    with open(storage_rs, "r") as f:
        content = f.read()

    # The new API should use Error::io_source() or Error::invalid_input()
    # instead of Error::IO { source: ..., location: ... }

    # Check for old pattern: Error::IO { source: ..., location: ... }
    assert "Error::IO {" not in content, "Should not use old Error::IO {{ ... }} pattern"

    # Check for new patterns
    assert "Error::io_source" in content or "Error::io(" in content, \
        "Should use new Error::io_source() or Error::io() API"

    # Check that snafu::location!() is not used (was removed in new API)
    assert "snafu::location!()" not in content, "Should not use snafu::location!() in new API"


def test_rust_namespace_error_propagation():
    """Check that rust/lancedb/src/database/namespace.rs uses ? operator"""
    namespace_rs = os.path.join(REPO, "rust/lancedb/src/database/namespace.rs")
    with open(namespace_rs, "r") as f:
        content = f.read()

    # The fix simplified error handling with the ? operator
    # Look for the pattern that indicates the fix was applied

    # Old pattern would have explicit .map_err() with Error::Runtime
    # New pattern uses ? operator directly

    # Check that declare_table is called with ? operator
    assert ".declare_table(declare_request).await?" in content, \
        "Should use ? operator for declare_table error propagation"


def test_cargo_check_passes():
    """FAIL-TO-PASS: cargo check should pass after fixes are applied."""
    result = run_cargo_check()

    # Build should succeed
    if result.returncode != 0:
        # Filter out warnings, only show errors
        lines = result.stderr.split("\n")
        errors = [l for l in lines if "error[" in l or ("error" in l.lower() and "warning" not in l.lower())]
        error_msg = "\n".join(errors[:20])  # Show first 20 errors
        raise AssertionError(f"cargo check failed with errors:\n{error_msg}")


def test_no_old_error_patterns_in_namespace():
    """Check that old error patterns are removed from python/src/namespace.rs"""
    namespace_rs = os.path.join(REPO, "python/src/namespace.rs")
    with open(namespace_rs, "r") as f:
        content = f.read()

    # Should not have the old multi-line Error::io pattern with Default::default()
    import re

    # Old pattern: Error::io(\n    format!(...),\n    Default::default(),\n)
    old_pattern = r'Error::io\(\s*format!\([^)]+\),\s*Default::default\(\),\s*\)'
    matches = re.findall(old_pattern, content, re.DOTALL)

    if matches:
        raise AssertionError(f"Found old error API pattern in namespace.rs: {matches[0][:100]}")


def test_snafu_location_removed():
    """Check that snafu::location!() calls are removed from storage_options.rs"""
    storage_rs = os.path.join(REPO, "python/src/storage_options.rs")
    with open(storage_rs, "r") as f:
        content = f.read()

    location_count = content.count("snafu::location!()")
    assert location_count == 0, f"Should remove all snafu::location!() calls, found {location_count}"


def test_cargo_toml_dependencies_updated():
    """Verify all lance dependencies are updated to rc.3 in Cargo.toml"""
    cargo_toml = os.path.join(REPO, "Cargo.toml")
    with open(cargo_toml, "r") as f:
        content = f.read()

    # Check for lance dependency lines
    lance_deps = [line for line in content.split("\n") if "lance" in line and "version" in line]

    for dep in lance_deps:
        # Skip if it's a comment
        if dep.strip().startswith("#"):
            continue
        assert "3.0.0-rc.3" in dep, f"Dependency should use rc.3: {dep.strip()}"


# ============================================================================
# PASS-TO-PASS TESTS - Repo CI gates (run on base commit, must pass before fix)
# ============================================================================


def test_repo_cargo_fmt():
    """Repo's Rust code passes formatting check (pass_to_pass)."""
    # Install rustfmt if not present
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        capture_output=True, cwd=REPO, timeout=60
    )
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_clippy():
    """Repo's Rust code passes clippy lints (pass_to_pass)."""
    # Install clippy if not present
    subprocess.run(
        ["rustup", "component", "add", "clippy"],
        capture_output=True, cwd=REPO, timeout=60
    )
    r = subprocess.run(
        ["cargo", "clippy", "--workspace", "--tests", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_check_workspace():
    """Repo's Rust workspace compiles with cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--workspace", "--tests"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
