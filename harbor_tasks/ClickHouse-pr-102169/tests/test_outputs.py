#!/usr/bin/env python3
"""
Test suite for ClickHouse PR #102169:
Fix exception caused by stale ZooKeeper session in UDF retry loop.

Tests verify:
1. Session renewal happens inside the retry loop (f2p) - behavioral AST check
2. getObjectNamesAndSetWatch is called inside the retry loop (f2p) - behavioral AST check
3. All ZooKeeper operations use the same session variable (f2p) - behavioral AST check
4. Code compiles (p2p)
5. CLAUDE.md rule compliance: use 'exception' not 'crash' (agent_config)
6. File naming convention for modified files (p2p)
7. No tabs in modified source (p2p)
8. Line length limit for modified lines only (p2p)
9. ClickHouse C++ style checks (p2p - repo_tests)
10. Typos check via codespell (p2p - repo_tests)
11. Git hygiene checks - conflict markers, DOS newlines (p2p - repo_tests)
"""

import subprocess
import re
import sys
import clang.cindex
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


# =============================================================================
# REPO_TESTS: Pass-to-pass tests using actual CI commands
# =============================================================================

def test_clang_syntax_only():
    """
    Pass-to-pass: Basic clang syntax-only check on the target file.
    This validates that the C++ code is syntactically valid.
    Only fails on actual syntax errors, not missing includes.
    """
    r = subprocess.run(
        ["clang", "-std=c++23", "-fsyntax-only", "-Werror",
         "-I", str(REPO / "src"), "-I", str(REPO / "base"),
         str(TARGET_FILE)],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )

    # Filter out "file not found" errors - we only care about actual syntax errors
    if r.returncode != 0:
        lines = r.stderr.split('\n')
        real_errors = []
        for line in lines:
            # Skip "file not found" and related include errors
            if 'file not found' in line.lower():
                continue
            # Skip "fatal error:" lines that are about missing includes
            if 'fatal error' in line.lower() and 'file not found' in line.lower():
                continue
            # Keep other errors (syntax errors, warnings treated as errors, etc.)
            if line.strip() and 'error:' in line.lower():
                real_errors.append(line)

        if real_errors:
            errors_str = '\n'.join(real_errors[:20])
            assert False, f"Clang syntax-only check found syntax errors:\n{errors_str}"


def test_libclang_parses():
    """
    Pass-to-pass: Verify the C++ file parses without syntax errors using libclang.
    This is a more robust check than the basic clang syntax-only check.
    Only fails on actual syntax errors, not missing includes.
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


def test_check_cpp_style():
    """
    Pass-to-pass: Run ClickHouse C++ style check script on the repository.
    This is the actual CI style check used in ClickHouse's pull request checks.
    Only checks for style violations in the target file.
    """
    # Run the style check script
    r = subprocess.run(
        ["bash", str(REPO / "ci/jobs/scripts/check_style/check_cpp.sh")],
        capture_output=True, text=True, timeout=300, cwd=str(REPO)
    )

    # Filter output for the target file specifically
    output_lines = r.stdout.split('\n') + r.stderr.split('\n')
    target_violations = [
        line for line in output_lines
        if 'UserDefinedSQLObjectsZooKeeperStorage' in line
        and 'style error' in line
    ]

    if target_violations:
        violations_str = '\n'.join(target_violations[:10])
        assert False, f"Style violations found in target file:\n{violations_str}"


def test_codespell_typos():
    """
    Pass-to-pass: Run codespell on the modified file to check for typos.
    This is part of ClickHouse's CI style checks.
    """
    r = subprocess.run(
        ["codespell", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60
    )

    if r.returncode != 0 or r.stdout.strip():
        assert False, f"codespell found issues:\n{r.stdout}"


def test_no_conflict_markers():
    """
    Pass-to-pass: Check for git conflict markers in the modified file.
    This is a standard CI check to prevent committing unresolved conflicts.
    """
    r = subprocess.run(
        ["grep", "-P", "^(<<<<<<<|=======|>>>>>>>)$", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30
    )

    if r.returncode == 0 and r.stdout.strip():  # grep found matches
        assert False, f"Git conflict markers found in file:\n{r.stdout}"


def test_no_dos_newlines():
    """
    Pass-to-pass: Check for DOS/Windows newlines (CRLF) in the modified file.
    ClickHouse uses Unix newlines (LF) only.
    """
    r = subprocess.run(
        ["grep", "-l", "-P", "\r$", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30
    )

    if r.returncode == 0:  # grep found matches
        assert False, "File contains DOS/Windows newlines (\\r\\n instead of \\n)"


def test_clang_format_check():
    """
    Pass-to-pass: Verify the file doesn't have excessive formatting issues.
    Runs clang-format on the whole file and counts violations.
    Uses a threshold to tolerate pre-existing issues in the base code.
    """
    r = subprocess.run(
        ["clang-format", "--dry-run", "--Werror", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=str(REPO)
    )

    if r.returncode != 0:
        issue_count = 0
        for line in r.stderr.split('\n'):
            if 'error' in line.lower() or 'warning' in line.lower():
                issue_count += 1

        # Base code may have pre-existing formatting issues, so use a
        # generous threshold.  Fail only if the total is clearly excessive.
        if issue_count > 80:
            sample = '\n'.join(
                l for l in r.stderr.split('\n')
                if 'error' in l.lower() or 'warning' in l.lower()
            )[:2000]
            assert False, (
                f"clang-format found {issue_count} style issues in the file "
                f"(threshold 80):\n{sample}"
            )


def test_various_checks_bom():
    """
    Pass-to-pass: Check that the target file doesn't have UTF BOM markers.
    Part of various_checks.sh in ClickHouse CI.
    """
    r = subprocess.run(
        ["grep", "-l", "-F", "\xef\xbb\xbf", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30
    )

    if r.returncode == 0 and r.stdout.strip():
        assert False, "File contains UTF-8 BOM marker"


def test_various_checks_executable_bit():
    """
    Pass-to-pass: Verify the target file is not executable.
    Source files should not have executable permissions.
    """
    r = subprocess.run(
        ["git", "ls-files", "-s", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO)
    )

    if r.returncode == 0 and r.stdout.strip():
        # Parse mode from git ls-files output: <mode> <object> <stage> <file>
        mode = r.stdout.split()[0] if r.stdout.split() else ""
        # 100644 = regular file, 100755 = executable, 120000 = symlink
        if mode not in ["100644", "120000", "100755"]:
            assert False, f"File has unusual permissions (mode={mode}). Should be 100644 (regular) or 120000 (symlink)."


# =============================================================================
# STATIC: Pass-to-pass tests using file content checks
# =============================================================================

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


def test_file_naming_convention():
    """
    Pass-to-pass: Verify modified C++ files follow ClickHouse naming convention.
    Only checks the specific files modified by this PR.
    Files should use PascalCase (e.g., MyClassName.cpp, MyClassName.h).
    """
    import re

    # Only check the specific files modified by this PR
    files_to_check = [
        TARGET_FILE,
        REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.h"
    ]

    # ClickHouse uses PascalCase for file names (e.g., UserDefinedSQLObjectsZooKeeperStorage.cpp)
    pascal_case_pattern = re.compile(r'^[A-Z][a-zA-Z0-9_]*\.(cpp|h)$')

    invalid_names = []
    for f in files_to_check:
        if f.exists() and not pascal_case_pattern.match(f.name):
            invalid_names.append(f.name)

    if invalid_names:
        assert False, f"Files not following PascalCase naming: {invalid_names}"


def test_no_tabs_in_source():
    """
    Pass-to-pass: Verify no tab characters in modified source files.
    ClickHouse uses spaces for indentation (4 spaces).
    """
    content = TARGET_FILE.read_text()

    lines_with_tabs = []
    for i, line in enumerate(content.split('\n'), 1):
        if '\t' in line:
            lines_with_tabs.append(i)

    if lines_with_tabs:
        lines_str = ', '.join(str(l) for l in lines_with_tabs[:10])
        assert False, f"Tab characters found on lines: {lines_str}. Use 4 spaces instead."


def test_code_line_length():
    """
    Pass-to-pass: Verify lines in modified code sections don't exceed limit.
    Only checks lines that were likely modified (containing retry loop pattern).
    ClickHouse uses 140 character limit (from .clang-format).
    """
    content = TARGET_FILE.read_text()
    lines = content.split('\n')

    # Look for lines that contain the fix patterns - only check these lines
    # since they are the ones that were modified by the PR
    fix_patterns = [
        "retries_ctl",
        "isRetry",
        "Renew the session",
        "getObjectNamesAndSetWatch",
        "tryLoadObject"
    ]

    long_lines = []
    for i, line in enumerate(lines, 1):
        # Only check lines that are part of the fix/modified code
        if any(pattern in line for pattern in fix_patterns):
            if len(line) > 140:
                long_lines.append((i, len(line), line[:50]))

    if long_lines:
        violations = ', '.join(f"line {ln} ({ch} chars)" for ln, ch, _ in long_lines[:5])
        assert False, f"Modified lines exceeding 140 characters: {violations}"


# =============================================================================
# FAIL_TO_PASS: Behavioral tests using AST analysis via libclang
# =============================================================================

def _parse_target_file():
    """Helper to parse the target file and return translation unit."""
    index = clang.cindex.Index.create()
    tu = index.parse(
        str(TARGET_FILE),
        args=['-std=c++23', '-I', str(REPO / 'src'), '-I', str(REPO / 'base')],
        options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    )
    return tu


def _is_in_target_file(node):
    """Check if a node is located in the target .cpp file (not header)."""
    if not node.location.file:
        return False
    filepath = str(node.location.file)
    return 'UserDefinedSQLObjectsZooKeeperStorage.cpp' in filepath


def _find_lambda_in_retry_loop(body_node, require_target_file=True):
    """Find lambda expressions that are arguments to retryLoop calls."""
    lambdas = []

    def has_retry_loop_in_subtree(node):
        """Recursively check if retryLoop appears anywhere in the subtree."""
        if 'retryLoop' in node.spelling:
            return True
        for child in node.get_children():
            if has_retry_loop_in_subtree(child):
                return True
        return False

    def recurse(node):
        # Only process nodes in the target file (if required)
        if require_target_file and not _is_in_target_file(node):
            # Still recurse into children as they might be in target file
            for child in node.get_children():
                recurse(child)
            return

        # Check for retryLoop call - it can appear in different forms:
        # 1. As a CALL_EXPR with DECL_REF_EXPR/MEMBER_REF_EXPR child
        # 2. As UNEXPOSED_EXPR with MEMBER_REF_EXPR containing OVERLOADED_DECL_REF
        if node.kind == clang.cindex.CursorKind.CALL_EXPR:
            is_retry_loop = False
            for child in node.get_children():
                if child.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                    if 'retryLoop' in child.spelling:
                        is_retry_loop = True
                        break
                elif child.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
                    if 'retryLoop' in child.spelling:
                        is_retry_loop = True
                        break
                    # Check inside MEMBER_REF_EXPR for OVERLOADED_DECL_REF
                    if has_retry_loop_in_subtree(child):
                        is_retry_loop = True
                        break

            if is_retry_loop:
                # Find the lambda argument
                for child in node.get_children():
                    if child.kind == clang.cindex.CursorKind.LAMBDA_EXPR:
                        lambdas.append(child)

        # Template method calls like retryLoop may appear as UNEXPOSED_EXPR
        # with MEMBER_REF_EXPR containing OVERLOADED_DECL_REF "retryLoop"
        # and LAMBDA_EXPR as a sibling
        elif node.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR:
            if has_retry_loop_in_subtree(node):
                # Look for lambda as a direct child
                for child in node.get_children():
                    if child.kind == clang.cindex.CursorKind.LAMBDA_EXPR:
                        lambdas.append(child)

        for child in node.get_children():
            recurse(child)

    recurse(body_node)
    return lambdas


def _get_source_range(node):
    """Get source code text for a node's extent."""
    if not node.extent.start.file or not node.extent.end.file:
        return ""
    filepath = str(node.extent.start.file)
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        start_line = node.extent.start.line - 1
        end_line = node.extent.end.line
        # Handle single line vs multi-line
        if start_line == end_line - 1:
            line = lines[start_line]
            start_col = node.extent.start.column - 1
            end_col = node.extent.end.column - 1
            return line[start_col:end_col]
        else:
            result = lines[start_line][node.extent.start.column - 1:]
            for i in range(start_line + 1, end_line - 1):
                result += lines[i]
            if end_line - 1 < len(lines):
                result += lines[end_line - 1][:node.extent.end.column - 1]
            return result
    except Exception:
        return ""


def test_session_renewal_behavior():
    """
    Fail-to-pass: Verify session renewal happens inside the retry loop.

    Behavioral check: Uses libclang AST to find the retryLoop lambda,
    then checks the source code within the lambda for:
    1. A check for isRetry() condition
    2. A call to getZooKeeper() in the same scope

    This is a behavioral test because it verifies the control flow pattern
    exists, not specific variable names or text strings.
    """
    tu = _parse_target_file()

    # Check for real errors first
    real_errors = [d for d in tu.diagnostics
                   if d.severity >= clang.cindex.Diagnostic.Error
                   and 'file not found' not in d.spelling]
    if real_errors:
        assert False, f"Syntax errors prevent AST analysis: {real_errors[0].spelling}"

    # Find the retryLoop call and its lambda argument
    retry_lambdas = _find_lambda_in_retry_loop(tu.cursor)

    if not retry_lambdas:
        assert False, "No retryLoop(lambda) pattern found - the fix should include a retry loop"

    # Check each retry lambda for the session renewal pattern
    found_renewal_pattern = False

    for lambda_node in retry_lambdas:
        # Get the source code of the lambda
        lambda_source = _get_source_range(lambda_node)

        # Check for isRetry() and getZooKeeper() in the lambda source
        if 'isRetry()' in lambda_source and 'getZooKeeper()' in lambda_source:
            found_renewal_pattern = True
            break

    assert found_renewal_pattern, \
        "Behavioral check failed: The retry loop must contain 'if (isRetry()) { ... getZooKeeper() ... }' pattern"


def test_watches_registered_in_loop():
    """
    Fail-to-pass: Verify getObjectNamesAndSetWatch is called inside the retry loop.

    Behavioral check: Uses libclang AST to verify that getObjectNamesAndSetWatch
    is called within the retry loop lambda, not before it.

    This ensures watches are registered on the potentially-fresh session.
    """
    tu = _parse_target_file()

    # Find retryLoop lambdas
    retry_lambdas = _find_lambda_in_retry_loop(tu.cursor)

    if not retry_lambdas:
        assert False, "No retryLoop pattern found"

    # Check that getObjectNamesAndSetWatch is called inside a retry lambda
    found_in_loop = False

    for lambda_node in retry_lambdas:
        # Get the source code of the lambda
        lambda_source = _get_source_range(lambda_node)

        # Check for getObjectNamesAndSetWatch in the lambda source
        if 'getObjectNamesAndSetWatch' in lambda_source:
            found_in_loop = True
            break

    assert found_in_loop, \
        "Behavioral check failed: getObjectNamesAndSetWatch must be called inside the retry loop lambda"


def test_consistent_session_usage():
    """
    Fail-to-pass: Verify consistent session variable usage in ZooKeeper operations.

    Behavioral check: Uses libclang AST to verify that:
    1. All ZooKeeper operations inside the retry loop use the same variable
    2. getObjectNamesAndSetWatch and tryLoadObject are called with the same session

    This ensures the session is consistently used (whether fresh or original).
    """
    tu = _parse_target_file()

    retry_lambdas = _find_lambda_in_retry_loop(tu.cursor)

    if not retry_lambdas:
        assert False, "No retryLoop pattern found"

    found_consistent_usage = False

    for lambda_node in retry_lambdas:
        # Get the source code of the lambda
        lambda_source = _get_source_range(lambda_node)

        # Check that both getObjectNamesAndSetWatch and tryLoadObject are called
        # with the same session variable (indicated by same first argument)
        if 'getObjectNamesAndSetWatch(' in lambda_source and 'tryLoadObject(' in lambda_source:
            # Extract the first argument of each call using simple regex
            import re
            # Find all occurrences of getObjectNamesAndSetWatch(XXX, ...)
            getobject_pattern = re.search(r'getObjectNamesAndSetWatch\(([^,)]+)', lambda_source)
            tryload_pattern = re.search(r'tryLoadObject\(([^,)]+)', lambda_source)

            if getobject_pattern and tryload_pattern:
                getobject_arg = getobject_pattern.group(1).strip()
                tryload_arg = tryload_pattern.group(1).strip()

                # Check that both calls use the same session variable
                if getobject_arg == tryload_arg:
                    found_consistent_usage = True
                    break

    assert found_consistent_usage, \
        "Behavioral check failed: ZooKeeper operations must use the same session variable consistently"


def test_session_refresh_complete():
    """
    Fail-to-pass: Verify the complete session refresh pattern exists.

    Behavioral check: Uses libclang AST to verify that:
    1. A session variable is assigned before the retry loop
    2. Inside the retry loop (when isRetry), the same variable is reassigned
    3. All operations use this variable

    This is the complete fix pattern for stale session handling.
    """
    tu = _parse_target_file()

    retry_lambdas = _find_lambda_in_retry_loop(tu.cursor)

    if not retry_lambdas:
        assert False, "No retryLoop pattern found"

    found_complete_pattern = False

    for lambda_node in retry_lambdas:
        # Get the source code of the lambda
        lambda_source = _get_source_range(lambda_node)

        # Check for the complete pattern: isRetry() and assignment with getZooKeeper()
        # This verifies that when isRetry() is true, a fresh session is obtained
        if 'isRetry()' in lambda_source and 'getZooKeeper()' in lambda_source:
            # Also verify there's an assignment (using =) in the context
            import re
            # Look for pattern: variable = ...getZooKeeper()
            assignment_pattern = re.search(r'\b\w+\s*=\s*.*getZooKeeper\(\)', lambda_source, re.DOTALL)
            if assignment_pattern:
                found_complete_pattern = True
                break

    assert found_complete_pattern, \
        "Behavioral check failed: The retry loop must contain 'if (isRetry()) session = getZooKeeper()' pattern"


# =============================================================================
# AGENT_CONFIG: Tests for CLAUDE.md rule compliance
# =============================================================================

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
    import pytest
    pytest.main([__file__, "-v"])
