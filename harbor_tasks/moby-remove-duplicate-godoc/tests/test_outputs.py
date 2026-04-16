#!/usr/bin/env python3
"""
Tests for moby/moby#52260 - Remove duplicate package doc, enable godoclint linter.

This PR:
1. Removes duplicate package documentation from local_unix.go and local_windows.go
2. Enables the godoclint linter in .golangci.yml
"""

import subprocess
import os
import sys

REPO = "/workspace/moby"


def test_godoclint_enabled_in_config():
    """Fail-to-pass: godoclint linter must be enabled in .golangci.yml"""
    config_path = os.path.join(REPO, ".golangci.yml")
    with open(config_path, 'r') as f:
        content = f.read()

    # Check that godoclint is in the linters list
    assert "godoclint" in content, "godoclint linter not found in .golangci.yml"

    # Verify it's not commented out
    for line in content.split('\n'):
        if 'godoclint' in line:
            assert not line.strip().startswith('#'), f"godoclint is commented out: {line}"


def test_unix_file_no_package_doc():
    """Fail-to-pass: local_unix.go must not have duplicate package doc comment"""
    file_path = os.path.join(REPO, "daemon/volume/local/local_unix.go")
    with open(file_path, 'r') as f:
        content = f.read()

    # The file should NOT contain the old package doc comment
    assert "// Package local provides the default implementation for volumes" not in content, \
        "Duplicate package doc still present in local_unix.go"

    # File should start with build tag, then package declaration
    lines = content.split('\n')
    # Find first non-empty, non-comment line that's not a build tag
    found_build_tag = False
    found_package = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('//'):
            if 'go:build' in stripped or 'build' in stripped:
                found_build_tag = True
            continue
        if stripped.startswith('package '):
            found_package = True
            break

    assert found_package, "Package declaration not found in local_unix.go"


def test_windows_file_no_package_doc():
    """Fail-to-pass: local_windows.go must not have duplicate package doc comment"""
    file_path = os.path.join(REPO, "daemon/volume/local/local_windows.go")
    with open(file_path, 'r') as f:
        content = f.read()

    # The file should NOT contain the old package doc comment
    assert "// Package local provides the default implementation for volumes" not in content, \
        "Duplicate package doc still present in local_windows.go"

    # File should have package declaration early
    lines = content.split('\n')
    found_package = False
    for line in lines[:10]:  # Check first 10 lines
        stripped = line.strip()
        if stripped.startswith('package '):
            found_package = True
            break

    assert found_package, "Package declaration not found near top of local_windows.go"


def test_local_package_has_proper_doc():
    """Pass-to-pass: The local package should still have documentation elsewhere"""
    # Check that local.go exists and has proper package doc
    local_go_path = os.path.join(REPO, "daemon/volume/local/local.go")
    if os.path.exists(local_go_path):
        with open(local_go_path, 'r') as f:
            content = f.read()
        # The main local.go should have the package doc
        assert "// Package local provides" in content, \
            "Package documentation missing from local.go (should be the canonical location)"


def test_golangci_config_valid():
    """Pass-to-pass: .golangci.yml must be valid YAML"""
    import yaml
    config_path = os.path.join(REPO, ".golangci.yml")
    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AssertionError(f"Invalid YAML in .golangci.yml: {e}")

    # Verify linters section exists
    assert 'linters' in config, "No linters section in .golangci.yml"
    linters = config.get('linters', {})
    assert 'enable' in linters, "No enable section in linters"
    assert 'godoclint' in linters['enable'], "godoclint not in enabled linters list"


def test_go_code_compiles():
    """Pass-to-pass: The modified Go code should compile"""
    r = subprocess.run(
        ["go", "build", "./daemon/volume/local/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Go code failed to compile:\n{r.stderr}"


def test_go_vet():
    """Pass-to-pass: Go vet passes on modified package (CI check)"""
    r = subprocess.run(
        ["go", "vet", "./daemon/volume/local/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Go vet failed:\n{r.stderr}"


def test_go_fmt():
    """Pass-to-pass: Go fmt passes on modified package (CI check)"""
    r = subprocess.run(
        ["go", "fmt", "./daemon/volume/local/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Go fmt failed:\n{r.stderr}"


def test_local_unit_tests():
    """Pass-to-pass: Unit tests for local volume package pass (CI check)"""
    # Run only tests that don't require mount permissions (skip mount-dependent tests)
    r = subprocess.run(
        ["go", "test", "-count=1", "-run", "TestGetAddress|TestGetPassword|TestValidateName|TestInitialize|TestRemove|TestReload|TestCreate$|TestQuota|TestVol", "./daemon/volume/local/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
