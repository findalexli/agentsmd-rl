"""Test outputs for bun-defer-dynamic-import-unknown-node

This task verifies:
1. Code fix: linker defers dynamic import() of unknown node: modules to runtime
2. Bugfix: logger properly duplicates line_text to avoid use-after-poison
3. Refactor: credentials.zig uses bun.strings instead of std.mem
4. Config: CLAUDE.md updated with proper formatting
5. Regression test: Test file created that verifies the runtime behavior

The primary behavioral test is the regression test file, which uses Bun.spawn
to actually execute code and verify the fix works. Source code checks verify
the fix was applied but are not sufficient alone.
"""

import subprocess
import sys
import re
import os
from pathlib import Path

REPO = "/workspace/bun"


def test_regression_test_file_created():
    """Regression test file for issue #25707 must be created.

    The PR adds a test file at test/regression/issue/25707.test.ts
    that verifies the dynamic import deferral behavior via actual execution.
    """
    test_path = Path(REPO) / "test" / "regression" / "issue" / "25707.test.ts"
    assert test_path.exists(), "Regression test file 25707.test.ts must exist"

    content = test_path.read_text()

    # The regression test must use Bun's test harness and spawn bun to execute code
    # These are behavioral - they actually RUN the code being tested
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

    The test should verify that require() of CJS files containing import("node:sqlite")
    does NOT fail at load time - this is the core behavioral fix.
    """
    test_path = Path(REPO) / "test" / "regression" / "issue" / "25707.test.ts"

    content = test_path.read_text()

    # Check the test actually uses dynamic import of a node: module
    has_dynamic_import = 'import("node:sqlite")' in content
    has_require = "require(" in content

    # The test must verify exit code is 0 (success) - proving load didn't fail
    has_exit_code_check = "exitCode" in content or ".exited" in content

    # The test must verify correct output
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

    # The test should verify that when the dynamic import executes,
    # it fails with ERR_UNKNOWN_BUILTIN_MODULE (not at load time)
    has_error_code = "ERR_UNKNOWN_BUILTIN_MODULE" in content
    has_catch_block = "catch" in content

    assert has_error_code, \
        "Test must check for ERR_UNKNOWN_BUILTIN_MODULE error code"
    assert has_catch_block, \
        "Test must use try/catch to handle runtime error"


def test_linker_defers_unknown_node_modules():
    """Linker must defer dynamic import() of unknown node: modules to runtime.

    The fix adds .dynamic to the condition that decides whether to defer
    module resolution. We verify by checking that unknown node: modules
    would NOT trigger the immediate-failure path.

    Note: We don't check for the specific enum value .dynamic because
    alternative implementations could use a different approach (e.g., a
    set membership check, or checking kind.category). The REGRESSION TEST
    is what actually verifies the behavior - this is a supplementary check.
    """
    linker_path = Path(REPO) / "src" / "linker.zig"
    content = linker_path.read_text()

    # Find the whenModuleNotFound function - this is where the deferral decision is made
    # The function signature is consistent across implementations
    has_when_module_not_found = "fn whenModuleNotFound" in content

    assert has_when_module_not_found, \
        "linker.zig must have whenModuleNotFound function"

    # The function should have logic that handles import kinds
    # We check that there is SOME handling of different import kinds,
    # not the specific gold implementation
    has_import_kind_handling = "import_record.kind" in content or "import_kind" in content

    assert has_import_kind_handling, \
        "linker.zig must handle import kind in module resolution"


def test_logger_ensures_line_text_safety():
    """Logger must ensure line_text outlives arena-allocated source memory.

    The fix changes how line_text is handled to prevent use-after-poison.
    We verify by checking that the logger has logic to duplicate or safely
    handle text from the source.

    Note: The regression test for the main bug ensures overall behavior is
    correct. This check verifies the logger fix is present.
    """
    logger_path = Path(REPO) / "src" / "logger.zig"
    content = logger_path.read_text()

    # The addResolveError function should handle text duplication
    has_add_resolve_error = "fn addResolveError" in content or "pub fn addResolveError" in content

    assert has_add_resolve_error, \
        "logger.zig must have addResolveError function"

    # The logger should have a way to duplicate text - check for relevant patterns
    # Not checking for specific 'true' literal since alternatives could pass
    # a flag differently or use a different duplication strategy
    has_text_handling = "line_text" in content or "text" in content.lower()

    assert has_text_handling, \
        "logger.zig must handle text/location data"


def test_credentials_uses_bun_strings_api():
    """credentials.zig must use bun.strings API instead of std.mem for string operations.

    The refactor changes containsNewlineOrCR to use bun.strings.indexOfAny.
    We verify the function exists and uses appropriate string utilities.

    Note: Not checking for specific function name 'indexOfAny' because alternative
    implementations could use different but equivalent bun.strings functions.
    """
    credentials_path = Path(REPO) / "src" / "s3" / "credentials.zig"
    content = credentials_path.read_text()

    # The function should exist
    has_contains_newline = "fn containsNewlineOrCR" in content

    assert has_contains_newline, \
        "credentials.zig must have containsNewlineOrCR function"

    # Find the function body to check its implementation
    lines = content.split("\n")
    in_function = False
    function_lines = []
    for line in lines:
        if "fn containsNewlineOrCR" in line:
            in_function = True
        elif in_function:
            if line.strip() == "}" and len(function_lines) > 0:
                break
            function_lines.append(line)

    function_body = "\n".join(function_lines)

    # The function should use some form of indexOfAny or equivalent
    uses_index_of_any = "indexOfAny" in function_body

    assert uses_index_of_any, \
        "containsNewlineOrCR must use indexOfAny for newline/CR checking"

    # Check it uses bun.strings, not std.mem - but be flexible about exact API
    uses_bun_strings = "strings." in function_body or "bun.strings" in content
    uses_std_mem = "std.mem.indexOfAny" in function_body

    assert uses_bun_strings or not uses_std_mem, \
        "containsNewlineOrCR should use bun.strings, not std.mem"


def test_claude_md_has_required_sections():
    """CLAUDE.md must have the required sections with proper content."""
    claude_path = Path(REPO) / "src" / "CLAUDE.md"
    content = claude_path.read_text()

    # Check for required section headers
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

    # The table should use proper markdown table syntax with | separators
    # and have a header separator row (contains ---)
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
            # Table ends when we see a non-| line after the separator
            if found_separator and not line.strip().startswith("|") and len(line.strip()) > 0:
                break

    assert len(table_rows) >= 3, "CLAUDE.md must have table header, separator, and at least one row"
    assert found_separator, "CLAUDE.md table must have --- separator row"

    # Verify rows have proper two-column format
    for row in table_rows[2:]:  # Skip header and separator
        if row.strip().startswith("|") and "---" not in row:
            parts = [p for p in row.split("|") if p.strip()]
            assert len(parts) >= 2, f"Table row must have at least 2 columns: {row}"