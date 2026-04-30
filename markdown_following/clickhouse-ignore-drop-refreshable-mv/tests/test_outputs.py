#!/usr/bin/env python3
"""Test suite for ClickHouse refreshable materialized views fix."""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Interpreters/InterpreterDropQuery.cpp")


def _run_clang_tidy(file_path: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run clang-tidy on a file to verify syntactic validity."""
    return subprocess.run(
        ["clang-tidy", "-checks=-*", file_path, "--"],
        capture_output=True, text=True, timeout=timeout, cwd=REPO
    )


def test_refreshable_view_guard():
    """Verify that refreshable materialized views are protected from DROP-to-TRUNCATE conversion (f2p)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that the file references StorageMaterializedView (behavior: we check this type)
    assert "StorageMaterializedView" in content, \
        "Missing reference to StorageMaterializedView"

    # Check that refreshability is tested (behavior: we call isRefreshable or similar)
    assert "isRefreshable" in content, \
        "Missing refreshability check"

    # Check that the ignore_drop_queries_probability condition has been extended with a guard
    lines = content.split('\n')
    guard_found = False
    for i, line in enumerate(lines):
        if "ignore_drop_queries_probability" in line:
            # Look at this line and prior lines for a negated guard condition
            context = ' '.join(lines[max(0, i - 2):i + 1])
            if '!' in context and ('&&' in context or '||' in context):
                guard_found = True
                break

    assert guard_found, \
        "Missing guard condition before ignore_drop_queries_probability check"

    # Verify the modified code is syntactically valid by running clang-tidy (subprocess)
    result = _run_clang_tidy(TARGET_FILE)
    combined = result.stdout + result.stderr
    syntax_errors = re.findall(r"error: (expected|syntax error|unmatched)", combined, re.IGNORECASE)
    assert not syntax_errors, f"Syntax errors in modified file: {syntax_errors[:3]}"


def test_truncate_behavior_documented():
    """Verify that the TRUNCATE problem is documented in a comment (f2p)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find comments in the file
    comments = re.findall(r'//[/!].*', content)

    # Check that at least one comment mentions both TRUNCATE and refresh-related behavior
    truncate_refresh_comment = False
    for comment in comments:
        lower = comment.lower()
        if 'truncate' in lower and ('refresh' in lower or 'orphan' in lower or 'background' in lower):
            truncate_refresh_comment = True
            break

    assert truncate_refresh_comment, \
        "Missing comment explaining why TRUNCATE is problematic for refreshable views"


def test_logic_structure():
    """Verify the logic structure: guard comes before the probability check (f2p)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')

    # Find where StorageMaterializedView-related code appears
    mv_line = -1
    prob_line = -1

    for i, line in enumerate(lines):
        if "StorageMaterializedView" in line and "dynamic_cast" in line:
            mv_line = i
        if "ignore_drop_queries_probability" in line:
            prob_line = i

    assert mv_line != -1, \
        "Missing refreshable materialized view check (StorageMaterializedView + dynamic_cast)"
    assert prob_line != -1, \
        "Missing ignore_drop_queries_probability reference"
    assert mv_line < prob_line, \
        "The refreshable materialized view check should happen before the probability condition"


def test_cpp_syntax_valid():
    """Verify that the C++ file has valid syntax (p2p)."""
    result = _run_clang_tidy(TARGET_FILE)

    error_patterns = [
        r"fatal error: .* file not found",
        r"error: expected",
        r"error: syntax error",
        r"error: unmatched",
    ]

    combined_output = result.stdout + result.stderr
    for pattern in error_patterns:
        matches = re.findall(pattern, combined_output, re.IGNORECASE)
        assert not matches, f"Syntax error found: {matches}"


def test_repo_cpp_structure_valid():
    """Repo's C++ files have valid structure (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for balanced braces
    open_count = content.count("{")
    close_count = content.count("}")
    assert open_count == close_count, f"Unbalanced braces: {open_count} vs {close_count}"

    # Check for balanced parentheses
    open_p = content.count("(")
    close_p = content.count(")")
    assert open_p == close_p, f"Unbalanced parens: {open_p} vs {close_p}"

    # Check no null bytes
    assert chr(0) not in content, "File contains null bytes"

    # Check valid UTF-8
    try:
        content.encode("utf-8")
    except UnicodeEncodeError as e:
        assert False, f"Invalid UTF-8: {e}"


def test_repo_clang_tidy_basic():
    """Repo's clang-tidy basic checks pass (pass_to_pass)."""
    # Run clang-tidy with minimal checks that don't require full build system
    r = subprocess.run(
        ["clang-tidy", "-checks=-*,-clang-diagnostic-unknown-argument",
         "-extra-arg=-Wno-unknown-pragmas",
         "-extra-arg=-Wno-unused-command-line-argument",
         TARGET_FILE, "--"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )

    combined = r.stdout + r.stderr

    # We expect "file not found" for includes since we're not in a proper build context
    # But we should NOT see syntax errors like "expected" or "syntax error"
    syntax_errors = re.findall(r"error: expected|error: syntax error|error: unmatched", combined)
    assert not syntax_errors, f"Syntax errors found: {syntax_errors[:3]}"


def test_repo_code_style_basic():
    """Repo's basic code style checks pass (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    # Check that file doesn't have trailing whitespace
    trailing_ws_count = 0
    for i, line in enumerate(lines, 1):
        if line.rstrip() != line:
            trailing_ws_count += 1

    # Too much trailing whitespace is a problem
    assert trailing_ws_count < 50, f"Too many lines with trailing whitespace: {trailing_ws_count}"

    # Check file starts with expected pattern
    first_line = lines[0] if lines else ""
    valid_starts = ['#include', '///', '/*', '#pragma', 'module']
    assert any(first_line.startswith(p) for p in valid_starts), \
        f"File doesn't start with expected pattern: {first_line[:50]}"


def test_repo_file_readable():
    """Repo's target file is readable and valid (pass_to_pass)."""
    # File exists
    assert os.path.exists(TARGET_FILE), f"Target file doesn't exist: {TARGET_FILE}"

    # File is readable
    assert os.access(TARGET_FILE, os.R_OK), f"Target file not readable: {TARGET_FILE}"

    # File has content
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert len(content) > 0, "Target file is empty"
    assert len(content) > 1000, "Target file seems too small"

    # Check for expected includes
    assert '#include' in content, "File missing any includes"

    # Check for namespace usage
    assert 'namespace DB' in content or 'namespace' in content, "File missing namespace"


def test_repo_no_duplicate_includes():
    """Repo's C++ files have no duplicate includes (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    includes = []
    for line in content.split('\n'):
        if re.match(r'^#include ', line):
            includes.append(line.strip())

    include_counts = {line: includes.count(line) for line in includes}
    duplicates = {line: count for line, count in include_counts.items() if count > 1}

    assert not duplicates, f"Found duplicate includes: {duplicates}"


def test_repo_yaml_syntax_valid():
    """Repo's YAML files have valid syntax (pass_to_pass)."""
    import yaml

    yaml_files = [
        os.path.join(REPO, ".github/workflows/pull_request.yml"),
        os.path.join(REPO, ".github/workflows/master.yml"),
    ]

    errors = []
    for yaml_file in yaml_files:
        if os.path.exists(yaml_file):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{yaml_file}: {e}")

    assert not errors, f"YAML syntax errors: {'; '.join(errors)}"


def test_repo_python_syntax_valid():
    """Repo's Python files have valid syntax (pass_to_pass)."""
    py_files = [
        os.path.join(REPO, "tests/clickhouse-test"),
        os.path.join(REPO, "ci/jobs/check_style.py"),
    ]

    errors = []
    for py_file in py_files:
        if os.path.exists(py_file):
            result = subprocess.run(
                ["python3", "-m", "py_compile", py_file],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{py_file}: {result.stderr[:200]}")

    assert not errors, f"Python syntax errors: {'; '.join(errors)}"
