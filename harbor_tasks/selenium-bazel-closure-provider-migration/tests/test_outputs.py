"""Tests for the Bazel Closure provider migration fix.

This verifies that javascript/private/header.bzl has been migrated from
deprecated struct field access to modern Starlark provider API.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/selenium")
TARGET_FILE = REPO / "javascript" / "private" / "header.bzl"


def test_file_exists():
    """Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_load_statement_present():
    """FAIL-TO-PASS: ClosureJsBinaryInfo must be loaded from rules_closure."""
    content = TARGET_FILE.read_text()

    # Check for the load statement
    load_pattern = r'load\("@rules_closure//closure/private:defs\.bzl",\s*"ClosureJsBinaryInfo"\)'
    assert re.search(load_pattern, content), (
        "Missing load statement for ClosureJsBinaryInfo. "
        "Expected: load(\"@rules_closure//closure/private:defs.bzl\", \"ClosureJsBinaryInfo\")"
    )


def test_no_deprecated_getattr():
    """FAIL-TO-PASS: Deprecated getattr pattern must be removed."""
    content = TARGET_FILE.read_text()

    # Old pattern: getattr(d, "closure_js_binary", None)
    assert 'getattr(d, "closure_js_binary"' not in content, (
        "Found deprecated getattr pattern. "
        "Replace getattr(d, 'closure_js_binary', None) with ClosureJsBinaryInfo in d"
    )


def test_new_provider_check_present():
    """FAIL-TO-PASS: New provider check pattern must be present."""
    content = TARGET_FILE.read_text()

    # New pattern: ClosureJsBinaryInfo in d
    assert "ClosureJsBinaryInfo in d" in content, (
        "Missing new provider check pattern. "
        "Expected: if ClosureJsBinaryInfo in d:"
    )


def test_no_deprecated_field_access():
    """FAIL-TO-PASS: Deprecated field access d.closure_js_binary.bin must be removed."""
    content = TARGET_FILE.read_text()

    # Old pattern: d.closure_js_binary.bin
    assert "d.closure_js_binary.bin" not in content, (
        "Found deprecated field access pattern. "
        "Replace d.closure_js_binary.bin with d[ClosureJsBinaryInfo].bin"
    )


def test_new_provider_access_present():
    """FAIL-TO-PASS: New provider access pattern must be present."""
    content = TARGET_FILE.read_text()

    # New pattern: d[ClosureJsBinaryInfo].bin
    assert "d[ClosureJsBinaryInfo].bin" in content, (
        "Missing new provider access pattern. "
        "Expected: d[ClosureJsBinaryInfo].bin"
    )


def test_bazel_syntax_valid():
    """FAIL-TO-PASS: Bazel file must have valid syntax (no undefined symbols)."""
    content = TARGET_FILE.read_text()

    # Check that ClosureJsBinaryInfo is used consistently
    # It should be mentioned in: load, `in` check, and [] access
    assert content.count("ClosureJsBinaryInfo") >= 3, (
        "ClosureJsBinaryInfo should appear at least 3 times: "
        "once in load(), once in 'in' check, once in [] access"
    )


def test_binary_dict_update_correct():
    """PASS-TO-PASS: The binaries.update() call should use correct provider access."""
    content = TARGET_FILE.read_text()

    # Look for the pattern: binaries.update({name: d[ClosureJsBinaryInfo].bin})
    update_pattern = r'binaries\.update\(\{name:\s*d\[ClosureJsBinaryInfo\]\.bin\}\)'
    assert re.search(update_pattern, content), (
        "The binaries.update() call should use d[ClosureJsBinaryInfo].bin"
    )


def test_provider_check_in_loop():
    """PASS-TO-PASS: Provider check should be inside the deps loop."""
    content = TARGET_FILE.read_text()

    # Verify the structure: for d in ctx.attr.deps: ... if ClosureJsBinaryInfo in d:
    loop_pattern = r'for\s+d\s+in\s+ctx\.attr\.deps:'
    assert re.search(loop_pattern, content), "Missing 'for d in ctx.attr.deps:' loop"

    # Find the indentation and structure
    lines = content.split('\n')
    in_loop = False
    found_provider_check = False

    for line in lines:
        if 'for d in ctx.attr.deps:' in line:
            in_loop = True
            continue
        if in_loop:
            # Check if this line is the provider check (indented under the loop)
            if 'ClosureJsBinaryInfo in d' in line:
                found_provider_check = True
                break
            # If we hit a non-indented line, we've exited the loop
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            if line.strip() and line.strip()[0].isalpha() and not line.startswith(' '):
                break

    assert found_provider_check, (
        "ClosureJsBinaryInfo in d check should be inside the 'for d in ctx.attr.deps' loop"
    )


def test_repo_build_files_exist():
    """PASS-TO-PASS: Required Bazel build files should exist."""
    # Check for MODULE.bazel or WORKSPACE
    module_bazel = REPO / "MODULE.bazel"
    workspace = REPO / "WORKSPACE"

    assert module_bazel.exists() or workspace.exists(), (
        "Repository should have MODULE.bazel or WORKSPACE file"
    )


def test_repo_bazel_query():
    """PASS-TO-PASS: Bazel query on javascript/private works (repo CI check)."""
    r = subprocess.run(
        ["bazel", "query", "//javascript/private:all"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel query failed:\n{r.stderr}"
    # Verify expected targets exist
    assert "//javascript/private:gen_file" in r.stdout, "Missing gen_file target"
    assert "//javascript/private:closure_make_deps" in r.stdout, "Missing closure_make_deps target"


def test_repo_bazel_build():
    """PASS-TO-PASS: Bazel build of javascript/private works (repo CI check)."""
    r = subprocess.run(
        ["bazel", "build", "//javascript/private:all"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel build failed:\n{r.stderr[-500:]}"


def test_repo_bazel_syntax_check():
    """PASS-TO-PASS: Starlark syntax in javascript/private is valid (repo CI check)."""
    # Build the specific target that uses header.bzl to validate syntax
    r = subprocess.run(
        ["bazel", "build", "//javascript/private:gen_file"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel syntax check failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
