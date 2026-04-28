#!/usr/bin/env python3
"""Test outputs for Hugo PR #14515: Replace deprecated parser.ParseDir and doc.New."""

import subprocess
import re
import sys
import os

REPO = "/workspace/hugo"
TARGET_FILE = "tpl/internal/templatefuncsRegistry.go"
TARGET_PATH = os.path.join(REPO, TARGET_FILE)


def test_no_deprecated_parser_parse_dir():
    """Fail-to-pass: parser.ParseDir should not be used (deprecated since Go 1.25)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    if re.search(r'parser\.ParseDir\s*\(', content):
        raise AssertionError("Found deprecated parser.ParseDir() call")


def test_no_deprecated_doc_new():
    """Fail-to-pass: doc.New should not be used (deprecated)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    if re.search(r'(?<!From)doc\.New\s*\(', content):
        raise AssertionError("Found deprecated doc.New() call")


def test_parse_dir_helper_exists():
    """Fail-to-pass: New unexported directory parsing helper function should exist."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for an unexported function that takes FileSet and dir and returns AST files
    if not re.search(r'func\s+[a-z]\w*\s*\([^)]*\*token\.FileSet[^)]*\)\s*\([^)]*\*ast\.File', content, re.DOTALL):
        raise AssertionError("Unexported directory parsing helper function not found with expected signature (takes *token.FileSet, returns AST files)")


def test_parse_dir_uses_parser_parse_file():
    """Fail-to-pass: Should use parser.ParseFile (non-deprecated)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    if not re.search(r'parser\.ParseFile\s*\(', content):
        raise AssertionError("parser.ParseFile should be used")


def test_uses_doc_new_from_files():
    """Fail-to-pass: Should use doc.NewFromFiles instead of doc.New."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    if not re.search(r'doc\.NewFromFiles\s*\(', content):
        raise AssertionError("Should use doc.NewFromFiles instead of doc.New")


def test_ast_import_added():
    """Fail-to-pass: go/ast package should be imported (needed for []*ast.File)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    if '"go/ast"' not in content:
        raise AssertionError("Missing import for go/ast package")


def test_parse_dir_not_exported():
    """Pass-to-pass: Helper function should not be exported (starts with lowercase)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    if re.search(r'func\s+ParseDir\s*\(', content):
        raise AssertionError("ParseDir should not be exported, use lowercase name")


def test_code_compiles():
    """Pass-to-pass: The modified code should compile successfully."""
    result = subprocess.run(
        ["go", "build", "./tpl/internal/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        raise AssertionError(f"Code compilation failed:\n{result.stderr}")


def test_package_tests_pass():
    """Pass-to-pass: Tests for tpl/internal should pass."""
    result = subprocess.run(
        ["go", "test", "./tpl/internal/...", "-v", "-count=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        if "no test files" not in result.stderr and "no tests to run" not in result.stdout:
            raise AssertionError(f"Tests failed:\n{result.stderr}\n{result.stdout}")


def test_check_script_compiles():
    """Fail-to-pass: The repo's check.sh (which runs staticcheck) should pass after the fix."""
    check_script = os.path.join(REPO, "check.sh")
    if not os.path.exists(check_script):
        result = subprocess.run(
            ["go", "vet", "./tpl/internal/..."],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise AssertionError(f"go vet failed:\n{result.stderr}")
        return

    result = subprocess.run(
        ["./check.sh", "./tpl/internal/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    if result.returncode != 0:
        raise AssertionError(f"check.sh failed:\n{result.stderr}\n{result.stdout}")


def test_repo_go_vet():
    """Repo's go vet passes on modified package (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./tpl/internal/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_repo_gofmt():
    """Repo's gofmt check passes on modified package (pass_to_pass)."""
    r = subprocess.run(
        ["gofmt", "-l", "tpl/internal/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if r.stdout.strip():
        raise AssertionError(f"gofmt found unformatted files:\n{r.stdout}")


def test_repo_build_all():
    """Repo's full build passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"go build ./... failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_check():
    """pass_to_pass | CI job 'test' → step 'Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_test():
    """pass_to_pass | CI job 'test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_build_for_dragonfly():
    """pass_to_pass | CI job 'test' → step 'Build for dragonfly'"""
    r = subprocess.run(
        ["bash", "-lc", 'go install\ngo clean -i -cache'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build for dragonfly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")