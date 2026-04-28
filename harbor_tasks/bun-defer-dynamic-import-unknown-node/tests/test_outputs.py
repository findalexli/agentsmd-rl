"""Test outputs for bun-defer-dynamic-import-unknown-node

This task verifies:
1. Code fix: linker defers dynamic import() of unknown node: modules to runtime
2. Bugfix: logger properly duplicates line_text to avoid use-after-poison
3. Refactor: credentials.zig uses bun.strings instead of std.mem
4. Config: CLAUDE.md updated with proper formatting
5. Regression test: Test file created that verifies the runtime behavior
"""

import subprocess
import sys
import re
import os
import tempfile
from pathlib import Path

REPO = "/workspace/bun"


def _find_zig_function_body(content, fn_name):
    """Find a Zig function body by exact function name.

    Returns the function body content (between outermost { and }).
    """
    lines = content.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Remove leading 'pub ' if present
        if stripped.startswith("pub "):
            check_line = stripped[4:]
        else:
            check_line = stripped

        # Match function name exactly
        if check_line.startswith(f"fn {fn_name}") or check_line == f"fn {fn_name}":
            # Collect lines until we find the matching closing brace
            brace_count = 0
            started = False
            body_lines = []
            for j in range(i, len(lines)):
                l = lines[j]
                if not started:
                    body_lines.append(l)
                    if '{' in l:
                        brace_count += l.count('{')
                        started = True
                else:
                    body_lines.append(l)
                    brace_count += l.count('{')
                    brace_count -= l.count('}')
                    if brace_count <= 0:
                        break
            full = "\n".join(body_lines)
            first_brace = full.index('{')
            last_brace = full.rindex('}')
            return full[first_brace+1:last_brace]
    return ""


def test_regression_test_file_created():
    """Regression test file for issue #25707 must be created.

    The PR adds a test file at test/regression/issue/25707.test.ts
    that verifies the dynamic import deferral behavior via actual execution.
    """
    test_path = Path(REPO) / "test" / "regression" / "issue" / "25707.test.ts"
    assert test_path.exists(), "Regression test file 25707.test.ts must exist"

    content = test_path.read_text()

    has_bun_exe = "bunExe()" in content
    has_bun_spawn = "Bun.spawn" in content
    has_temp_dir = "tempDir" in content
    has_harness_import = 'from "harness"' in content

    assert has_harness_import, "Test must import from harness (bunExe, bunEnv, tempDir)"
    assert has_bun_exe, "Test must use bunExe() to locate Bun executable"
    assert has_bun_spawn, "Test must use Bun.spawn() to run code in subprocess"
    assert has_temp_dir, "Test must use tempDir() for isolated test files"


def test_linker_defers_unknown_node_modules():
    """Linker must defer dynamic import() of unknown node: modules to runtime.

    The fix modifies the deferral condition to include .dynamic import kind
    alongside .require and .require_resolve.
    """
    linker_path = Path(REPO) / "src" / "linker.zig"
    content = linker_path.read_text()
    lines = content.split("\n")

    # Find the deferral condition that handles .require and .require_resolve
    # The fix adds .dynamic to this same condition
    deferral_context = []
    for i, line in enumerate(lines):
        if ".require" in line and ("or" in line or "==" in line):
            start = max(0, i - 1)
            end = min(len(lines), i + 4)
            deferral_context = lines[start:end]
            break

    deferral_text = "\n".join(deferral_context)

    has_require = ".require" in deferral_text
    has_require_resolve = ".require_resolve" in deferral_text
    has_dynamic_in_deferral = ".dynamic" in deferral_text

    assert has_require and has_require_resolve, (
        "Deferral condition should handle .require and .require_resolve"
    )
    assert has_dynamic_in_deferral, (
        "Deferral condition should include .dynamic (the fix). "
        f"Found context: {deferral_text[:300]}"
    )


def test_logger_ensures_line_text_safety():
    """Logger must ensure line_text outlives arena-allocated source memory.

    The fix changes the text_dupe parameter from false to true in addResolveError
    so that line_text is duplicated and survives arena reset.
    """
    logger_path = Path(REPO) / "src" / "logger.zig"
    content = logger_path.read_text()

    function_body = _find_zig_function_body(content, "addResolveError")

    assert function_body, "Could not find addResolveError function body"

    # The fix: text_dupe parameter changed from false to true
    has_true_param = "addResolveErrorWithLevel" in function_body and ", true, .err" in function_body
    has_comment_about_dup = "dupe" in function_body or "outlives" in function_body

    assert has_true_param or has_comment_about_dup, (
        "addResolveError should pass 'true' for text_dupe parameter or have a comment about duplicating line_text. "
        f"Function body:\n{function_body}"
    )


def test_credentials_uses_bun_strings_api():
    """credentials.zig must use bun.strings API instead of std.mem.

    The fix replaces std.mem.indexOfAny with strings.indexOfAny in
    containsNewlineOrCR. Verify the function no longer uses std.mem.
    """
    credentials_path = Path(REPO) / "src" / "s3" / "credentials.zig"
    content = credentials_path.read_text()

    function_body = _find_zig_function_body(content, "containsNewlineOrCR")

    uses_std_mem = "std.mem.indexOfAny" in function_body

    assert not uses_std_mem, (
        "containsNewlineOrCR should NOT use std.mem.indexOfAny. "
        "The fix replaces std.mem with bun.strings for string operations."
    )

    uses_bun_strings = "strings.indexOfAny" in function_body or "bun.strings" in function_body

    assert uses_bun_strings, (
        "containsNewlineOrCR should use strings.indexOfAny (from bun.strings). "
        "Expected: strings.indexOfAny(value, \"\\r\\n\")."
    )


def test_credentials_has_strings_import():
    """credentials.zig must import the strings module from bun.

    The file uses bun.strings APIs throughout and should have the proper
    import: const strings = bun.strings;
    """
    credentials_path = Path(REPO) / "src" / "s3" / "credentials.zig"
    content = credentials_path.read_text()

    assert "const strings = bun.strings" in content, (
        "credentials.zig must import strings from bun.strings"
    )


def test_claude_md_has_required_sections():
    """CLAUDE.md must have the required sections with proper content."""
    claude_path = Path(REPO) / "src" / "CLAUDE.md"
    content = claude_path.read_text()

    required_sections = [
        "Key functions (all take `bun.FileDescriptor`",
        "Key methods:",
        "For pooled path buffers (avoids 64KB stack allocations on Windows):"
    ]

    for section in required_sections:
        assert section in content, f"CLAUDE.md must have section: {section}"


def test_claude_md_table_formatting():
    """CLAUDE.md 'Instead of / Use' table must be properly formatted.

    The fix ensures the table has properly aligned columns with expanded
    separator lines. The old compact format (|-----------|-----|) must be
    replaced with the aligned format that has spaces and wider columns.
    """
    claude_path = Path(REPO) / "src" / "CLAUDE.md"
    content = claude_path.read_text()

    lines = content.split("\n")

    table_rows = []
    in_table = False
    found_separator = False
    separator_row = ""

    for line in lines:
        if "| Instead of" in line:
            in_table = True
        if in_table:
            table_rows.append(line)
            if "---" in line and line.strip().startswith("|"):
                found_separator = True
                separator_row = line
            if found_separator and not line.strip().startswith("|") and len(line.strip()) > 0:
                break

    assert len(table_rows) >= 3, (
        "CLAUDE.md must have table header, separator, and at least one row. "
        f"Found {len(table_rows)} table rows."
    )
    assert found_separator, "CLAUDE.md table must have --- separator row with pipe delimiters"

    # The new format has spaces between pipes and dashes: | --- |
    # The old compact format has no spaces: |---|
    assert "| -" in separator_row, (
        "CLAUDE.md table separator must use the expanded format with spaces "
        "between pipes and dashes (e.g. | ------ | not |------|). "
        f"Found separator: '{separator_row.strip()}'"
    )

    # The expanded separator should be significantly wider than the old format (~22 chars)
    assert len(separator_row.strip()) > 40, (
        f"CLAUDE.md table separator row must be wide (>40 chars). "
        f"Found: {len(separator_row.strip())} chars in '{separator_row.strip()}'"
    )

    for row in table_rows[2:]:
        if row.strip().startswith("|") and "---" not in row:
            parts = [p for p in row.split("|") if p.strip()]
            assert len(parts) >= 2, f"Table row must have at least 2 columns: {row}"


def test_claude_md_whitespace_improvements():
    """CLAUDE.md must have blank lines after section headers.

    The fix adds blank lines after:
    - "Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):"
    - "Key methods:"
    - "For pooled path buffers (avoids 64KB stack allocations on Windows):"
    """
    claude_path = Path(REPO) / "src" / "CLAUDE.md"
    content = claude_path.read_text()
    lines = content.split("\n")

    headers_to_check = [
        "Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):",
        "Key methods:",
        "For pooled path buffers (avoids 64KB stack allocations on Windows):",
    ]

    for header in headers_to_check:
        found = False
        for i, line in enumerate(lines):
            if line.strip() == header:
                found = True
                # Next line should be blank (empty or whitespace-only)
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                assert next_line.strip() == "", (
                    f"CLAUDE.md must have a blank line after '{header}'. "
                    f"Found: '{next_line}'"
                )
                break
        assert found, f"CLAUDE.md must contain section header: {header}"


# === PR-added subprocess tests ===

def test_pr_added_require_of_CJS_file_containing_dynamic_import_of():
    """fail_to_pass | PR added test 'require() of CJS file containing dynamic import of non-existent node: module does not fail at load time' in 'test/regression/issue/25707.test.ts'"""
    r = subprocess.run(
        ["bash", "-lc",
         "bun test ./test/regression/issue/25707.test.ts "
         r"-t 'require\(\) of CJS file containing dynamic import of non-existent node: module does not fail at load time'"],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_pr_added_require_of_CJS_file_with_bare_dynamic_import_of_():
    """fail_to_pass | PR added test 'require() of CJS file with bare dynamic import of non-existent node: module does not fail at load time' in 'test/regression/issue/25707.test.ts'"""
    r = subprocess.run(
        ["bash", "-lc",
         "bun test ./test/regression/issue/25707.test.ts "
         r"-t 'require\(\) of CJS file with bare dynamic import of non-existent node: module does not fail at load time'"],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_pr_added_dynamic_import_of_non_existent_node_module_in_CJ():
    """fail_to_pass | PR added test 'dynamic import of non-existent node: module in CJS rejects at runtime with correct error' in 'test/regression/issue/25707.test.ts'"""
    r = subprocess.run(
        ["bash", "-lc",
         "bun test ./test/regression/issue/25707.test.ts "
         "-t 'dynamic import of non-existent node: module in CJS rejects at runtime with correct error'"],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
