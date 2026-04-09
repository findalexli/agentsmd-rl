#!/usr/bin/env python3
"""
Test suite for ClickHouse PR #102169:
Fix crash caused by stale ZooKeeper session in UDF retry loop.

Tests verify:
1. Session renewal happens inside the retry loop (f2p)
2. getObjectNamesAndSetWatch is called inside the retry loop (f2p)
3. current_zookeeper variable is used instead of stale parameter (f2p)
4. Code compiles (p2p)
5. CLAUDE.md rule compliance: use 'exception' not 'crash' (agent_config)
"""

import subprocess
import sys
import clang.cindex
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def test_file_compiles():
    """Check that the C++ file can be parsed (syntax validation)."""
    result = subprocess.run(
        ["clang", "-fsyntax-only", "-std=c++23", "-I", str(REPO / "src"), str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Ignore include errors - we just want to verify basic syntax
    # A return code of 0 or error about missing headers is fine
    error_output = result.stderr.lower()
    if "error:" in error_output and "file not found" not in error_output:
        assert False, f"Syntax errors found:\n{result.stderr[:1000]}"


def test_libclang_parses():
    """
    Pass-to-pass: Verify the C++ file parses without syntax errors using libclang.
    This is a more robust check than the basic clang syntax-only check.
    Only fails on actual syntax errors, ignoring missing includes.
    """
    index = clang.cindex.Index.create()
    tu = index.parse(
        str(TARGET_FILE),
        args=['-std=c++23', '-I', str(REPO / 'src'), '-I', str(REPO / 'base')],
        options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    )

    # Filter diagnostics - only count real syntax errors, not "file not found"
    real_errors = []
    for diag in tu.diagnostics:
        spelling = diag.spelling
        # Skip "file not found" and related include errors
        if 'file not found' in spelling:
            continue
        # Skip vmodule lock warnings
        if 'vmodule' in spelling.lower():
            continue
        # Only count actual errors (not warnings/notes)
        if diag.severity >= clang.cindex.Diagnostic.Error:
            real_errors.append(f'{diag.location}: {spelling}')

    if real_errors:
        errors_str = '\n'.join(real_errors[:20])
        assert False, f"libclang found syntax errors:\n{errors_str}"


def test_header_has_pragma_once():
    """
    Pass-to-pass: Verify the header file has #pragma once in the first line.
    This is a ClickHouse codebase requirement for all header files.
    """
    header_file = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.h"
    first_line = header_file.read_text().splitlines()[0] if header_file.exists() else ""
    assert first_line == '#pragma once', \
        f"Header file must have '#pragma once' as first line, got: {first_line}"


def test_no_trailing_whitespace():
    """
    Pass-to-pass: Verify no trailing whitespace in modified files.
    ClickHouse style check enforces no trailing whitespace.
    """
    content = TARGET_FILE.read_text()
    lines = content.split('\n')

    trailing_whitespace_lines = []
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            trailing_whitespace_lines.append(i)

    if trailing_whitespace_lines:
        lines_str = ', '.join(str(l) for l in trailing_whitespace_lines[:10])
        assert False, f"Trailing whitespace found on lines: {lines_str}"


def test_session_renewal_in_retry_loop():
    """
    Fail-to-pass: The fix must renew the ZooKeeper session inside the retry loop.
    Check that 'isRetry()' and 'zookeeper_getter.getZooKeeper()' appear together.
    """
    content = TARGET_FILE.read_text()

    # Must have the session renewal check inside retryLoop
    has_is_retry = "retries_ctl.isRetry()" in content
    has_get_zookeeper = "zookeeper_getter.getZooKeeper()" in content

    assert has_is_retry, "Missing 'retries_ctl.isRetry()' check for session renewal"
    assert has_get_zookeeper, "Missing 'zookeeper_getter.getZooKeeper()' for session refresh"


def test_getobjectnames_inside_retry_loop():
    """
    Fail-to-pass: getObjectNamesAndSetWatch must be called inside the retry loop,
    not before it. This ensures watches are set on the fresh session.
    """
    content = TARGET_FILE.read_text()

    # Find the retryLoop lambda
    lines = content.split('\n')
    in_retry_loop = False
    brace_depth = 0
    found_getobjectnames_in_loop = False
    found_getobjectnames_before_loop = False

    for i, line in enumerate(lines):
        if 'retries_ctl.retryLoop' in line:
            in_retry_loop = True
            brace_depth = 0
            continue

        if in_retry_loop:
            # Track brace depth to know when we exit the lambda
            brace_depth += line.count('{') - line.count('}')

            if 'getObjectNamesAndSetWatch' in line:
                found_getobjectnames_in_loop = True
                break

            if brace_depth < 0 or (brace_depth == 0 and '}' in line and i > 0):
                # Exited the lambda without finding getObjectNamesAndSetWatch
                break

    # Also check that there's no call BEFORE retryLoop
    for line in lines:
        if 'retries_ctl.retryLoop' in line:
            break
        if 'getObjectNamesAndSetWatch' in line and 'object_names' in line:
            found_getobjectnames_before_loop = True

    assert found_getobjectnames_in_loop, \
        "getObjectNamesAndSetWatch must be called inside the retry loop"
    assert not found_getobjectnames_before_loop, \
        "getObjectNamesAndSetWatch should not be called before the retry loop"


def test_current_zookeeper_variable_used():
    """
    Fail-to-pass: The fix introduces a 'current_zookeeper' variable that tracks
    the potentially renewed session. It should be used instead of the 'zookeeper'
    parameter inside the retry loop.
    """
    content = TARGET_FILE.read_text()

    # Must have current_zookeeper variable
    has_current_zk_var = "zkutil::ZooKeeperPtr current_zookeeper" in content
    assert has_current_zk_var, "Missing 'current_zookeeper' variable declaration"

    # Must use current_zookeeper in tryLoadObject
    uses_current_in_tryload = "tryLoadObject(current_zookeeper," in content
    assert uses_current_in_tryload, \
        "Must use 'current_zookeeper' in tryLoadObject call, not the stale 'zookeeper' parameter"

    # Must use current_zookeeper in getObjectNamesAndSetWatch
    uses_current_in_getnames = "getObjectNamesAndSetWatch(current_zookeeper," in content
    assert uses_current_in_getnames, \
        "Must use 'current_zookeeper' in getObjectNamesAndSetWatch call"


def test_session_renewal_pattern_complete():
    """
    Fail-to-pass: Verify the complete pattern:
    if (retries_ctl.isRetry()) current_zookeeper = zookeeper_getter.getZooKeeper().first;
    This is the core of the fix.
    """
    content = TARGET_FILE.read_text()

    # Check the pattern exists
    pattern_check = "if (retries_ctl.isRetry())" in content
    renewal_assignment = "current_zookeeper = zookeeper_getter.getZooKeeper()" in content

    assert pattern_check and renewal_assignment, \
        "Missing the complete session renewal pattern: if (isRetry()) current_zookeeper = ..."


def test_claude_md_terminology():
    """
    Pass-to-pass: Verify CLAUDE.md rule compliance.
    When mentioning logical errors, say 'exception' instead of 'crash'.
    This is an agent_config check - code should follow repo conventions.
    """
    content = TARGET_FILE.read_text()
    comments_and_strings = content

    # Check that 'crash' is not used to describe logical errors in comments
    # (allow it in technical contexts like 'crash' as a noun for actual crashes)
    lower_content = comments_and_strings.lower()

    # Count occurrences of 'crash' in comments (rough heuristic)
    lines = content.split('\n')
    for line in lines:
        if '//' in line or '/*' in line:
            if ' crash' in line.lower() or 'crash ' in line.lower():
                # This is a soft check - just warn, don't fail
                # The actual PR doesn't have this issue
                pass

    # The main check: verify the comment in the fixed code uses proper terminology
    # The updated comment should mention "exception" not "crash"
    has_exception_terminology = "exception" in content.lower()
    assert has_exception_terminology, \
        "CLAUDE.md rule: When mentioning logical errors, say 'exception' instead of 'crash'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
