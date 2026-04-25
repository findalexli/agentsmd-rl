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
            # body_lines contains everything from function signature to closing brace
            # Extract content between first { and last }
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


def test_regression_test_exercises_dynamic_import():
    """Regression test must exercise dynamic import() of unknown node: modules.

    The test verifies that require() of CJS files containing import("node:sqlite")
    does NOT fail at load time - this is the core behavioral fix.
    """
    test_path = Path(REPO) / "test" / "regression" / "issue" / "25707.test.ts"

    content = test_path.read_text()

    has_dynamic_import = 'import("node:sqlite")' in content
    has_require = "require(" in content
    has_exit_code_check = "exitCode" in content or ".exited" in content
    has_expectations = "expect(" in content

    assert has_dynamic_import, \
        "Test must exercise dynamic import of node:sqlite module"
    assert has_require, \
        "Test must use require() to load CJS file"
    assert has_exit_code_check, \
        "Test must verify exit code (load succeeded)"
    assert has_expectations, \
        "Test must have expect() assertions"


def test_regression_test_verifies_error_at_runtime():
    """Regression test must verify ERR_UNKNOWN_BUILTIN_MODULE is caught at runtime.

    The fix defers the error to runtime - the test must verify this behavior.
    """
    test_path = Path(REPO) / "test" / "regression" / "issue" / "25707.test.ts"

    content = test_path.read_text()

    has_error_code = "ERR_UNKNOWN_BUILTIN_MODULE" in content
    has_catch_block = "catch" in content

    assert has_error_code, \
        "Test must check for ERR_UNKNOWN_BUILTIN_MODULE error code"
    assert has_catch_block, \
        "Test must use try/catch to handle runtime error"


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
            # Capture surrounding context
            start = max(0, i - 1)
            end = min(len(lines), i + 4)
            deferral_context = lines[start:end]
            break

    deferral_text = "\n".join(deferral_context)

    # The fix should add .dynamic to the same condition as .require and .require_resolve
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

    The fix changes the text_dupe parameter from false to true in addResolveError.
    We verify the fix by checking that the function now passes 'true' for text duplication.
    """
    logger_path = Path(REPO) / "src" / "logger.zig"
    content = logger_path.read_text()

    # Find the addResolveError function body
    function_body = _find_zig_function_body(content, "addResolveError")

    assert function_body, "Could not find addResolveError function body"

    # Check for the key fix: the function body should call addResolveErrorWithLevel
    # with 'true' for the text duplication parameter
    # In the original: false is passed
    # In the fix: true is passed

    # Check for true being passed to addResolveErrorWithLevel
    has_true_param = "addResolveErrorWithLevel" in function_body and ", true, .err" in function_body

    # Also check for comment about text duplication
    has_comment_about_dup = ("dupe" in function_body or "outlives" in function_body)

    assert has_true_param or has_comment_about_dup, (
        "addResolveError should pass 'true' for text_dupe parameter or have a comment about duplicating line_text. "
        f"Function body:\n{function_body}"
    )


def test_credentials_uses_bun_strings_api():
    """credentials.zig must use bun.strings API instead of std.mem.

    The fix replaces std.mem.indexOfAny with strings.indexOfAny in containsNewlineOrCR.
    We verify the bug is fixed by checking the function no longer uses std.mem.
    """
    credentials_path = Path(REPO) / "src" / "s3" / "credentials.zig"
    content = credentials_path.read_text()

    function_body = _find_zig_function_body(content, "containsNewlineOrCR")

    uses_std_mem = "std.mem.indexOfAny" in function_body

    # After the fix, std.mem should NOT be used in this function
    assert not uses_std_mem, (
        "containsNewlineOrCR should NOT use std.mem.indexOfAny. "
        "The fix replaces std.mem with bun.strings for string operations."
    )

    uses_bun_strings = "strings.indexOfAny" in function_body or "bun.strings" in function_body

    assert uses_bun_strings, (
        "containsNewlineOrCR should use strings.indexOfAny (from bun.strings). "
        "Expected: strings.indexOfAny(value, \"\\r\\n\")."
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

    The fix ensures the table has consistent column alignment with proper
    separator lines.
    """
    claude_path = Path(REPO) / "src" / "CLAUDE.md"
    content = claude_path.read_text()

    lines = content.split("\n")

    table_rows = []
    in_table = False
    found_separator = False

    for line in lines:
        if "| Instead of" in line or "Instead of |" in line:
            in_table = True
        if in_table:
            table_rows.append(line)
            if "---" in line:
                found_separator = True
            if found_separator and not line.strip().startswith("|") and len(line.strip()) > 0:
                break

    assert len(table_rows) >= 3, "CLAUDE.md must have table header, separator, and at least one row"
    assert found_separator, "CLAUDE.md table must have --- separator row"

    for row in table_rows[2:]:
        if row.strip().startswith("|") and "---" not in row:
            parts = [p for p in row.split("|") if p.strip()]
            assert len(parts) >= 2, f"Table row must have at least 2 columns: {row}"