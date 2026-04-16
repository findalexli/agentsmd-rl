"""
Test the rustls crypto provider fix in chroma tracing crate.

This tests that:
1. The rustls crypto provider is properly declared and initialized before OTLP TLS config
"""

import subprocess
import sys
import os
import json

REPO = "/workspace/chroma"
TRACING_DIR = os.path.join(REPO, "rust", "tracing")


def test_repo_cargo_check_tracing():
    """Rust code compiles with cargo check (pass-to-pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "chroma-tracing"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_fmt_tracing():
    """Rust code is properly formatted (pass-to-pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check", "--package", "chroma-tracing"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_clippy_tracing():
    """Rust code passes clippy linting (pass-to-pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--package", "chroma-tracing"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


def test_repo_cargo_doc_tests_tracing():
    """Rust doc tests pass (pass-to-pass)."""
    r = subprocess.run(
        ["cargo", "test", "--doc", "--package", "chroma-tracing"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo doc tests failed:\n{r.stderr[-500:]}"


def test_rustls_workspace_direct_dependency():
    """Verify rustls with aws-lc-rs is a direct workspace dependency (fail-to-pass)."""
    import tomllib

    workspace_cargo = os.path.join(REPO, "Cargo.toml")
    with open(workspace_cargo, 'rb') as f:
        data = tomllib.load(f)

    # Workspace dependencies are in workspace.dependencies
    workspace = data.get('workspace', {})
    deps = workspace.get('dependencies', {})
    rustls_dep = deps.get('rustls')
    assert rustls_dep is not None, "rustls not found as direct workspace dependency"

    # Check version and aws-lc-rs feature
    if isinstance(rustls_dep, dict):
        assert rustls_dep.get('version', '').startswith('0.23.37'), \
            f"rustls version should be 0.23.x, got {rustls_dep.get('version')}"
        features = rustls_dep.get('features', [])
        assert 'aws-lc-rs' in features, "aws-lc-rs feature not found in rustls dependency"


def test_tracing_cargo_toml_declares_rustls():
    """Verify chroma-tracing Cargo.toml declares rustls as workspace dependency (fail-to-pass)."""
    import tomllib
    tracing_cargo = os.path.join(TRACING_DIR, "Cargo.toml")
    with open(tracing_cargo, 'rb') as f:
        data = tomllib.load(f)

    rustls_dep = data.get('dependencies', {}).get('rustls')
    assert rustls_dep is not None, "rustls not found in chroma-tracing dependencies"

    # Must be a workspace dependency (dict with workspace=true) or at minimum exist
    if isinstance(rustls_dep, dict):
        assert rustls_dep.get('workspace') == True, "rustls should be a workspace dependency"
