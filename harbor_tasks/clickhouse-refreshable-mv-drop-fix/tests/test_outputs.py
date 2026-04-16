"""
Tests for ClickHouse refreshable materialized view DROP fix.

This verifies that DROP queries are not converted to TRUNCATE for
refreshable materialized views, which would cause them to keep
refreshing indefinitely and consume background pool threads.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Interpreters/InterpreterDropQuery.cpp")


def test_target_file_exists():
    """Target file exists and is readable."""
    assert os.path.exists(TARGET_FILE), f"Target file not found: {TARGET_FILE}"


def test_storage_materialized_view_include():
    """StorageMaterializedView header is included."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the include directive
    assert '#include <Storages/StorageMaterializedView.h>' in content, \
        "StorageMaterializedView header not included"


def test_refreshable_view_check_present():
    """The refreshable view check logic is present in executeToTableImpl."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the distinctive comment explaining the fix
    assert "Don't ignore DROP for refreshable materialized views" in content, \
        "Refreshable MV comment not found"

    # Check for the dynamic_cast to StorageMaterializedView
    assert "dynamic_cast<StorageMaterializedView *>(table.get())" in content, \
        "StorageMaterializedView dynamic_cast not found"

    # Check for the isRefreshable() call
    assert "isRefreshable()" in content, \
        "isRefreshable() check not found"

    # Check for the is_refreshable_view variable
    assert "is_refreshable_view" in content, \
        "is_refreshable_view variable not found"


def test_logic_condition_includes_refreshable_check():
    """The DROP-to-TRUNCATE condition excludes refreshable views."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the if condition that handles ignore_drop_queries_probability
    # After the fix, it should include "!is_refreshable_view"
    pattern = r'if\s*\(\s*!secondary_query\s*&&\s*!is_refreshable_view'
    match = re.search(pattern, content)

    assert match is not None, \
        "The condition does not include !is_refreshable_view check. " \
        "The fix requires adding '&& !is_refreshable_view' to prevent DROP-to-TRUNCATE conversion for refreshable views."


def test_comment_explains_rationale():
    """The comment explains why refreshable views need special handling."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for key phrases in the comment
    comment_section = content[content.find("Don't ignore DROP"):content.find("Don't ignore DROP") + 300]

    assert "TRUNCATE" in comment_section, "Comment should mention TRUNCATE"
    assert "refresh" in comment_section.lower(), "Comment should mention refresh"


def test_syntax_valid_cpp():
    """File contains valid C++ syntax (no obvious syntax errors)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for balanced braces in the function
    # Find executeToTableImpl and check brace balance in the relevant section
    start = content.find("BlockIO InterpreterDropQuery::executeToTableImpl")
    assert start != -1, "executeToTableImpl function not found"

    # Check for basic C++ syntax issues
    # Count braces to verify basic structure
    section = content[start:start + 5000]
    open_braces = section.count('{')
    close_braces = section.count('}')

    # The initial section should have balanced braces
    assert abs(open_braces - close_braces) <= 5, \
        f"Potential unbalanced braces: {open_braces} open, {close_braces} close"


def test_no_sleep_in_code():
    """Code does not use sleep to fix race conditions (per ClickHouse coding standards)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Per AGENTS.md: "Never use sleep in C++ code to fix race conditions - this is stupid and not acceptable!"
    sleep_pattern = re.search(r'\bsleep\s*\(|std::this_thread::sleep_for|usleep\s*\(', content, re.IGNORECASE)
    assert sleep_pattern is None, "Code contains sleep() which is not acceptable for race condition fixes"


def test_allman_braces_style():
    """Code uses Allman-style braces (opening brace on new line)."""
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    # Check a sample of control structures for Allman style
    # Look for patterns like "if (...)\n{" not "if (...) {"
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue

        # Check for control structures with opening braces on same line (K&R style)
        # This is a heuristic - we look for common patterns
        if re.search(r'\b(if|for|while|else)\s*.*\{[^}]*$', stripped):
            # Allow single-line statements like "if (x) { return; }"
            if not (stripped.endswith('}') and '{' in stripped):
                # Check if the previous non-empty line ends with )
                prev_idx = i - 1
                while prev_idx >= 0 and lines[prev_idx].strip() == '':
                    prev_idx -= 1
                if prev_idx >= 0:
                    prev_line = lines[prev_idx].strip()
                    if prev_line.endswith(')') or prev_line.endswith('const'):
                        # This is potentially Allman style - opening brace should be on its own line
                        # If current line has { after control structure, it's K&R
                        if re.search(r'\b(if|for|while)\s*\([^)]+\)\s*\{', stripped):
                            assert False, f"Line {i+1} appears to use K&R brace style instead of Allman: {stripped[:60]}"


def test_code_compiles_with_clang():
    """Code can be parsed by clang without syntax errors."""
    # Run clang-tidy or clang-check for syntax validation
    # This is a lightweight compilation check
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++23", "-I", f"{REPO}/src",
         "-I", f"{REPO}/base", "-I", f"{REPO}/contrib",
         "-c", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # We expect this to have some errors due to missing includes,
    # but we want to verify basic syntax is valid
    # Check for syntax errors specifically
    syntax_errors = [line for line in result.stderr.split('\n')
                     if 'error:' in line and 'syntax' in line.lower()]

    assert len(syntax_errors) == 0, \
        f"Syntax errors found: {syntax_errors[:3]}"


def test_repo_cpp_style_check():
    """Repo's C++ style check script passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert r.returncode == 0, f"C++ style check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_mypy_ci_scripts():
    """Repo's CI Python scripts pass mypy type check (pass_to_pass)."""
    # Install mypy first
    subprocess.run(["pip3", "install", "--break-system-packages", "mypy"],
                   capture_output=True, timeout=60)
    r = subprocess.run(
        ["mypy", "--config-file", f"{REPO}/tests/ci/.mypy.ini",
         f"{REPO}/tests/ci/env_helper.py",
         f"{REPO}/tests/ci/cache_utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"mypy check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_yamllint_workflows():
    """Repo's GitHub workflow files pass yamllint (pass_to_pass)."""
    # Install yamllint first
    subprocess.run(["pip3", "install", "--break-system-packages", "yamllint"],
                   capture_output=True, timeout=60)
    r = subprocess.run(
        ["yamllint", "-c", f"{REPO}/.yamllint", f"{REPO}/.github/workflows/pull_request.yml"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert r.returncode == 0, f"yamllint check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_python_syntax():
    """Repo's CI Python scripts have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/tests/ci/env_helper.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"
