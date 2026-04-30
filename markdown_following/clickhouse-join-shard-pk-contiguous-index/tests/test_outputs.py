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


def test_buggy_range_for_removed():
    """
    Fail-to-pass: The buggy range-for over parts_with_ranges that preserves
    original (potentially gapped) part indices must be removed.

    The original code used range-based iteration which copies parts from
    parts_with_ranges with their original part_index_in_query values.
    After filterPartsByQueryConditionCache drops parts in selectRangesToRead(),
    these values can be non-contiguous, causing wrong JOIN results.
    """
    content = TARGET_FILE.read_text()

    # The buggy pattern that preserves original part indices with gaps:
    # for (const auto & part : analysis_result->parts_with_ranges)
    buggy_range_for = r"for\s*\(\s*const\s+auto\s+&\s+part\s*:\s*analysis_result->parts_with_ranges\s*\)"
    assert not re.search(buggy_range_for, content), \
        "Buggy pattern still present: range-for over parts_with_ranges that preserves gaps"

    # The fix must still iterate over parts_with_ranges (but contiguously)
    assert "parts_with_ranges" in content, \
        "parts_with_ranges access missing from the fix"


def test_contiguous_part_index_handling():
    """
    Fail-to-pass: The fix uses indexed access to parts_with_ranges for
    contiguous part_index_in_query assignment instead of range-for.

    When parts are dropped by filterPartsByQueryConditionCache, the
    original range-for preserves non-contiguous part_index_in_query values.
    The fix must assign contiguous values starting from added_parts.
    """
    content = TARGET_FILE.read_text()

    # The fix must use indexed access: analysis_result->parts_with_ranges[...]
    assert re.search(r"analysis_result->parts_with_ranges\s*\[", content), \
        "Fix must use indexed access to parts_with_ranges (analysis_result->parts_with_ranges[idx])"

    # The fix must assign part_index_in_query contiguously from a counter
    # Pattern: part_index_in_query = <base> + <counter>
    assert re.search(r"part_index_in_query\s*=\s*\w+\s*\+\s*\w+", content), \
        "Fix must assign contiguous part_index_in_query values (part_index_in_query = base + counter)"

    # The base must be added_parts (the count of previously collected parts)
    assert "added_parts" in content, \
        "Fix missing added_parts reference for contiguous index assignment"


def test_qcc_interaction_comment():
    """
    Fail-to-pass: The fix includes a comment describing the interaction with
    filterPartsByQueryConditionCache.

    The bug only manifests when the query condition cache has previously
    cached filter results, causing selectRangesToRead() to drop some parts.
    The fix should document this interaction.
    """
    content = TARGET_FILE.read_text()

    # Find a comment or line mentioning the cache interaction near the fix
    assert "filterPartsByQueryConditionCache" in content, \
        "Fix must mention filterPartsByQueryConditionCache in explanation"


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

    # Missing includes produce "fatal error:" lines — those are expected at this stage.
    # Real syntax/parse errors produce "error:" (without "fatal") lines — those must fail.
    if result.returncode != 0:
        stderr_lower = result.stderr.lower()
        real_errors = [line for line in stderr_lower.split('\n')
                       if 'error:' in line and 'fatal error:' not in line]
        assert not real_errors, \
            f"Code has syntax/parse errors:\n{result.stderr[:500]}"


def test_target_file_exists():
    """
    Pass-to-pass: Target file exists in expected location.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_no_raw_pointers_in_fix_area():
    """
    Pass-to-pass: Verify the fix area doesn't introduce unsafe raw pointer usage.
    Only checks when the fix (indexed access + contiguous assignment) is present.
    """
    content = TARGET_FILE.read_text()

    # Find the fixed section (around the indexed access to parts_with_ranges)
    if re.search(r"analysis_result->parts_with_ranges\s*\[", content):
        # Extract the fixed for-loop section with indexed access
        match = re.search(
            r"for\s*\([^)]+\)\s*\{[^}]+\}",
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
    Fail-to-pass: Verify analysis_result->parts_with_ranges is accessed
    via indexed lookup rather than range-for iteration.
    """
    content = TARGET_FILE.read_text()

    # Should access analysis_result->parts_with_ranges with index, not range-for
    assert re.search(r"analysis_result->parts_with_ranges\s*\[", content), \
        "Fix should access parts_with_ranges by index (analysis_result->parts_with_ranges[idx])"


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_stateless_test_sql_present():
    """pass_to_pass | The stateless SQL test file from PR 101960 exists"""
    sql_test = REPO / "tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql"
    assert sql_test.exists(), f"SQL test file not found: {sql_test}"
    content = sql_test.read_text()
    assert "04065" in content, "Test identifier not found in SQL test"
    assert "JOIN" in content, "SQL test does not contain JOIN statement"

def test_ci_stateless_test_reference_matches():
    """pass_to_pass | The reference file has expected output 0 1 0 0"""
    ref_file = REPO / "tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.reference"
    assert ref_file.exists(), f"Reference file not found: {ref_file}"
    content = ref_file.read_text().strip()
    assert "0\t1\t0\t0" in content or "0 1 0 0" in content, \
        f"Reference output mismatch, expected 0 1 0 0, got: {content}"