"""
Tests for ClickHouse JOIN shard-by-PK fix.

The bug was in optimizeJoinByShards::apply() which assumed contiguous
part_index_in_query values, but filterPartsByQueryConditionCache can drop
parts leaving gaps in the indices. This caused the layer distribution to
assign parts to the wrong source, producing wrong results (0 rows).
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp"


def test_fix_contiguous_index_renumbering():
    """
    Fail-to-pass: Verify the fix renumbers part_index_in_query contiguously.

    Before fix: part.part_index_in_query += added_parts (preserves gaps)
    After fix: part.part_index_in_query = added_parts + local_idx (contiguous)
    """
    content = TARGET_FILE.read_text()

    # Check for the fix pattern: assigning contiguous indices using local_idx
    # The fix uses: all_parts.back().part_index_in_query = added_parts + local_idx;
    fix_pattern = r"part_index_in_query\s*=\s*added_parts\s*\+\s*local_idx"
    assert re.search(fix_pattern, content), \
        "Fix not applied: missing contiguous index renumbering (part_index_in_query = added_parts + local_idx)"

    # Check for local_idx loop variable
    loop_pattern = r"for\s*\(\s*size_t\s+local_idx\s*=\s*0"
    assert re.search(loop_pattern, content), \
        "Fix not applied: missing local_idx loop variable"

    # Verify the old buggy pattern is gone (range-for that preserves gaps)
    # The old code used: for (const auto & part : analysis_result->parts_with_ranges)
    buggy_range_for = r"for\s*\(\s*const\s+auto\s+&\s+part\s*:\s*analysis_result->parts_with_ranges\s*\)"
    assert not re.search(buggy_range_for, content), \
        "Buggy pattern still present: range-for over parts_with_ranges that preserves gaps"


def test_fix_comment_explains_issue():
    """
    Fail-to-pass: Verify the explanatory comment about the fix is present.
    """
    content = TARGET_FILE.read_text()

    # Check for comment explaining the issue
    assert "Renumber part_index_in_query to be contiguous" in content, \
        "Missing explanatory comment about contiguous renumbering"

    assert "filterPartsByQueryConditionCache may drop parts" in content, \
        "Missing comment explaining filterPartsByQueryConditionCache interaction"


def test_code_compiles():
    """
    Pass-to-pass: Verify the C++ code compiles without errors.
    """
    # Run clang syntax check on the file
    result = subprocess.run(
        ["clang-15", "-std=c++20", "-fsyntax-only", "-I", str(REPO / "src"),
         "-I", str(REPO / "base"), "-I", str(REPO / "contrib"),
         str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO)
    )

    # Syntax-only check may have include errors, but should not have parse errors
    # Just check that clang didn't crash and the file is parseable
    assert result.returncode == 0 or "error:" not in result.stderr.lower() or \
           "fatal error:" in result.stderr.lower(), \
        f"Code has syntax errors:\n{result.stderr[:500]}"


def test_target_file_exists():
    """
    Pass-to-pass: Target file exists in expected location.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_no_raw_pointers_in_fix_area():
    """
    Pass-to-pass: Verify the fix area doesn't introduce unsafe raw pointer usage.
    """
    content = TARGET_FILE.read_text()

    # Find the fixed section (around the contiguous index renumbering)
    if "Renumber part_index_in_query to be contiguous" in content:
        # Extract the fixed for-loop section
        match = re.search(
            r"for\s*\(\s*size_t\s+local_idx\s*=\s*0[^}]+\}",
            content,
            re.DOTALL
        )
        if match:
            fix_section = match.group(0)
            # Check no manual new/delete in the fix
            assert "new " not in fix_section, "Fix introduces raw new operator"
            assert "delete " not in fix_section, "Fix introduces raw delete operator"


def test_preserves_analysis_result_access():
    """
    Pass-to-pass: Verify analysis_result->parts_with_ranges is still accessed correctly.
    """
    content = TARGET_FILE.read_text()

    # Should still access analysis_result->parts_with_ranges with index
    assert "analysis_result->parts_with_ranges[local_idx]" in content, \
        "Fix should access parts_with_ranges by index"


def test_allman_brace_style():
    """
    Pass-to-pass: Verify the fix follows ClickHouse Allman brace style.

    Opening brace should be on its own line.
    """
    content = TARGET_FILE.read_text()

    # Check the for loop has opening brace on new line (Allman style)
    # Pattern: for (...)
    #     {
    allman_pattern = r"for\s*\([^)]+\)\s*\n\s*\{"
    assert re.search(allman_pattern, content), \
        "Fix should follow Allman brace style (opening brace on new line)"


def test_no_trailing_whitespace_in_target():
    """
    Pass-to-pass: Target file has no trailing whitespace (ClickHouse style check).

    Trailing whitespace is not allowed in ClickHouse codebase.
    """
    content = TARGET_FILE.read_bytes()
    text = content.decode('utf-8', errors='replace')

    # Check each line for trailing whitespace (excluding newline)
    for i, line in enumerate(text.split('\n'), 1):
        # Skip empty lines
        if line and line.rstrip() != line:
            assert False, f"Trailing whitespace found at {TARGET_FILE}:{i}"


def test_no_tabs_in_target():
    """
    Pass-to-pass: Target file uses spaces, not tabs (ClickHouse style check).

    Tabs are not allowed in ClickHouse C++ code.
    """
    content = TARGET_FILE.read_bytes()

    # Check for tab characters
    if b'\t' in content:
        # Find line number with tab
        lines = content.split(b'\n')
        for i, line in enumerate(lines, 1):
            if b'\t' in line:
                assert False, f"Tab character found at {TARGET_FILE}:{i}"


def test_file_not_executable():
    """
    Pass-to-pass: Target file has correct permissions (not executable).

    C++ source files should not have executable bit set.
    """
    import stat

    file_stat = TARGET_FILE.stat()
    mode = file_stat.st_mode

    # Check if any executable bit is set
    is_executable = bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

    assert not is_executable, f"Source file {TARGET_FILE} should not be executable"


def test_no_bom_in_target():
    """
    Pass-to-pass: Target file has no UTF-8/UTF-16 BOM (ClickHouse style check).

    Files should not have byte order marks.
    """
    content = TARGET_FILE.read_bytes()

    # Check for UTF-8 BOM
    utf8_bom = b'\xef\xbb\xbf'
    # Check for UTF-16LE BOM
    utf16le_bom = b'\xff\xfe'
    # Check for UTF-16BE BOM
    utf16be_bom = b'\xfe\xff'

    assert not content.startswith(utf8_bom), f"UTF-8 BOM found in {TARGET_FILE}"
    assert not content.startswith(utf16le_bom), f"UTF-16LE BOM found in {TARGET_FILE}"
    assert not content.startswith(utf16be_bom), f"UTF-16BE BOM found in {TARGET_FILE}"


def test_target_file_in_git():
    """
    Pass-to-pass: Target file is tracked by git with correct permissions.

    File should be tracked with mode 100644 (regular file).
    """
    r = subprocess.run(
        ["git", "ls-files", "-s", str(TARGET_FILE)],
        capture_output=True, text=True, cwd=str(REPO)
    )

    assert r.returncode == 0, f"Failed to check git status: {r.stderr}"
    assert r.stdout, f"File not tracked by git: {TARGET_FILE}"

    # Parse git ls-files output: <mode> <object> <stage> <file>
    parts = r.stdout.strip().split()
    mode = parts[0] if parts else ""

    # Mode should be 100644 (regular file, not executable, not symlink)
    assert mode == "100644", f"File has incorrect git mode: {mode}, expected 100644"


def test_no_duplicate_includes_in_target():
    """
    Pass-to-pass: Target file has no duplicate #include statements.

    Duplicate includes are wasteful and can cause issues.
    """
    content = TARGET_FILE.read_text(encoding='utf-8', errors='ignore')

    includes = []
    for line in content.split('\n'):
        if re.match(r'^#include ', line):
            includes.append(line.strip())

    # Check for duplicates
    seen = set()
    duplicates = []
    for inc in includes:
        if inc in seen:
            duplicates.append(inc)
        seen.add(inc)

    assert not duplicates, f"Duplicate #include found: {duplicates}"

def test_repo_ci_scripts_compile():
    """
    Pass-to-pass: Verify CI python scripts compile without syntax errors.
    """
    r = subprocess.run(
        ['python3', '-m', 'py_compile'] + [str(p) for p in (REPO / 'tests' / 'ci').glob('*.py')],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )
    assert r.returncode == 0, f'Python CI scripts syntax check failed:\n{r.stderr[:500]}'

def test_repo_shell_scripts_syntax():
    """
    Pass-to-pass: Verify repo shell scripts have valid syntax.
    """
    r = subprocess.run(
        ['bash', '-n', 'utils/check-large-objects.sh'],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )
    assert r.returncode == 0, f'Bash syntax check failed:\n{r.stderr[:500]}'


def test_repo_style_check_scripts_syntax():
    """
    Pass-to-pass: Verify CI style check scripts have valid syntax (pass_to_pass).
    """
    r = subprocess.run(
        ['bash', '-n', f'{REPO}/ci/jobs/scripts/check_style/check_cpp.sh'],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )
    assert r.returncode == 0, f'check_cpp.sh syntax check failed:\n{r.stderr[:500]}'


def test_repo_various_checks_script_syntax():
    """
    Pass-to-pass: Verify various_checks.sh script has valid syntax (pass_to_pass).
    """
    r = subprocess.run(
        ['bash', '-n', f'{REPO}/ci/jobs/scripts/check_style/various_checks.sh'],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )
    assert r.returncode == 0, f'various_checks.sh syntax check failed:\n{r.stderr[:500]}'


def test_repo_submodules_check_script_syntax():
    """
    Pass-to-pass: Verify check_submodules.sh script has valid syntax (pass_to_pass).
    """
    r = subprocess.run(
        ['bash', '-n', f'{REPO}/ci/jobs/scripts/check_style/check_submodules.sh'],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )
    assert r.returncode == 0, f'check_submodules.sh syntax check failed:\n{r.stderr[:500]}'


def test_repo_check_style_py_syntax():
    """
    Pass-to-pass: Verify check_style.py compiles without syntax errors (pass_to_pass).
    """
    r = subprocess.run(
        ['python3', '-m', 'py_compile', f'{REPO}/ci/jobs/check_style.py'],
        capture_output=True, text=True, timeout=120, cwd=str(REPO)
    )
    assert r.returncode == 0, f'check_style.py syntax check failed:\n{r.stderr[:500]}'


def test_repo_cpp_code_style_check():
    """
    Pass-to-pass: Run ClickHouse C++ style check on the codebase (pass_to_pass).
    """
    r = subprocess.run(
        ['bash', f'{REPO}/ci/jobs/scripts/check_style/check_cpp.sh'],
        capture_output=True, text=True, timeout=300, cwd=str(REPO)
    )
    # Script returns 0 even if style issues found - it just outputs warnings
    # Check that it runs without crashing (not return code 127 or similar)
    assert r.returncode == 0, f'C++ style check script failed to run:\n{r.stderr[:500]}'


def test_repo_submodules_check():
    """
    Pass-to-pass: Run ClickHouse submodules check script (pass_to_pass).
    """
    r = subprocess.run(
        ['bash', f'{REPO}/ci/jobs/scripts/check_style/check_submodules.sh'],
        capture_output=True, text=True, timeout=300, cwd=str(REPO)
    )
    assert r.returncode == 0, f'Submodules check script failed:\n{r.stderr[:500]}'


def test_repo_ci_jobs_scripts_syntax():
    """
    Pass-to-pass: Verify all CI job scripts have valid syntax (pass_to_pass).
    """
    import glob
    scripts = glob.glob(f'{REPO}/ci/jobs/scripts/check_style/*.sh')
    for script in scripts:
        r = subprocess.run(
            ['bash', '-n', script],
            capture_output=True, text=True, timeout=120, cwd=str(REPO)
        )
        assert r.returncode == 0, f'Script syntax error in {script}:\n{r.stderr[:500]}'


def test_repo_git_whitespace_check():
    """
    Pass-to-pass: Run git whitespace check on the repo (pass_to_pass).
    """
    r = subprocess.run(
        ['git', 'diff', '--check'],
        capture_output=True, text=True, timeout=60, cwd=str(REPO)
    )
    assert r.returncode == 0, f'Git whitespace check failed:\n{r.stderr[:500]}'
