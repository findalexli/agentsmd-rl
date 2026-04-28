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

    # Check that parser.ParseDir is not called as a function
    # Use word boundary to avoid matching in comments or strings
    # Pattern matches 'parser.ParseDir' followed by '(' (actual function call)
    if re.search(r'parser\.ParseDir\s*\(', content):
        raise AssertionError("Found deprecated parser.ParseDir() call - should use parseDir helper instead")


def test_no_deprecated_doc_new():
    """Fail-to-pass: doc.New should not be used (deprecated)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for the deprecated doc.New call (but not doc.NewFromFiles)
    # Use negative lookbehind to ensure it's not doc.NewFromFiles
    if re.search(r'(?<!From)doc\.New\s*\(', content):
        raise AssertionError("Found deprecated doc.New() call - should use doc.NewFromFiles() instead")


def test_parse_dir_helper_exists():
    """Fail-to-pass: New parseDir helper function should exist."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for an unexported function that takes FileSet and dir and returns AST files
    # Look for: func parseDir(...) ... *ast.File
    # More flexible than exact signature - allows alternative implementations
    if not re.search(r'func\s+parseDir\s*\([^)]*\*token\.FileSet[^)]*\)\s*\([^)]*\*ast\.File', content, re.DOTALL):
        raise AssertionError("parseDir helper function not found with expected signature (*token.FileSet, dir) returns []*ast.File")


def test_parse_dir_uses_parser_parse_file():
    """Fail-to-pass: parseDir should use parser.ParseFile (non-deprecated)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check that parser.ParseFile is called somewhere in the file
    # This verifies the new API is actually used
    if not re.search(r'parser\.ParseFile\s*\(', content):
        raise AssertionError("parser.ParseFile should be used - deprecated parser.ParseDir must be replaced")


def test_uses_doc_new_from_files():
    """Fail-to-pass: Should use doc.NewFromFiles instead of doc.New."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for doc.NewFromFiles usage - more flexible pattern
    # Allows different variable names and formatting
    if not re.search(r'doc\.NewFromFiles\s*\(\s*fset\s*,\s*\w+', content):
        raise AssertionError("Should use doc.NewFromFiles(fset, <files>, ...) instead of doc.New")


def test_ast_import_added():
    """Fail-to-pass: go/ast package should be imported (needed for []*ast.File)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for go/ast import
    if '"go/ast"' not in content:
        raise AssertionError("Missing import for go/ast package")


def test_parse_dir_not_exported():
    """Pass-to-pass: parseDir should not be exported (starts with lowercase)."""
    with open(TARGET_PATH, 'r') as f:
        content = f.read()

    # Check that ParseDir (exported) is not defined
    if re.search(r'func\s+ParseDir\s*\(', content):
        raise AssertionError("ParseDir should not be exported, use lowercase parseDir")

    # Verify lowercase parseDir exists
    if not re.search(r'func\s+parseDir\s*\(', content):
        raise AssertionError("parseDir function should exist with lowercase name")


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
    """Pass-to-pass: Tests for tpl/internal should pass (if any exist)."""
    result = subprocess.run(
        ["go", "test", "./tpl/internal/...", "-v", "-count=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # If tests don't exist or fail to compile, that's a failure
    if result.returncode != 0:
        # Only fail if it's a compilation error or actual test failure
        # Skip if no tests found
        if "no test files" not in result.stderr and "no tests to run" not in result.stdout:
            raise AssertionError(f"Tests failed:\n{result.stderr}\n{result.stdout}")


def test_check_script_compiles():
    """Pass-to-pass: The repo's check.sh should compile the package."""
    # First check if check.sh exists
    check_script = os.path.join(REPO, "check.sh")
    if not os.path.exists(check_script):
        # Fallback: just run go vet
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

    # Run check.sh for just the tpl/internal package
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
    # gofmt -l should output nothing if all files are formatted correctly
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
def test_ci_test_brew():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'brew install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_pandoc():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pandoc -v'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install mingw'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_staticcheck():
    """pass_to_pass | CI job 'test' → step 'Run staticcheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'export STATICCHECK_CACHE="${{ runner.temp }}/staticcheck"\nstaticcheck ./...\nrm -rf ${{ runner.temp }}/staticcheck'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Run staticcheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check():
    """pass_to_pass | CI job 'test' → step 'Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'sass --version;\nmage -v check;'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_test():
    """pass_to_pass | CI job 'test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v test'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_build_for_dragonfly():
    """pass_to_pass | CI job 'test' → step 'Build for dragonfly'"""
    r = subprocess.run(
        ["bash", "-lc", 'go install\ngo clean -i -cache'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Build for dragonfly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")