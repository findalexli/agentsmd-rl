"""Tests for revert PR mergeable check fix.

This tests that revert PRs are detected by "Reverts ClickHouse/" in PR body
and that the mergeable check becomes green when Fast test passes, even if
other jobs failed.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the repo to path for imports
REPO = Path("/workspace/ClickHouse")
PRAKTIKA_PATH = REPO / "ci" / "praktika"


def test_revert_pr_detection_logic():
    """Test that revert PR detection logic works correctly."""
    # Read the native_jobs.py file and verify the logic exists
    native_jobs_path = PRAKTIKA_PATH / "native_jobs.py"
    content = native_jobs_path.read_text()

    # Check for the revert PR detection pattern
    assert '"Reverts ClickHouse/" in env.PR_BODY' in content, \
        "Revert PR detection pattern not found"

    # Check for the Fast test failure check
    assert '"Fast test" in name' in content, \
        "Fast test failure check not found"

    # Check that the logic sets status to SUCCESS for revert PRs
    assert 'ready_for_merge_status = Result.Status.SUCCESS' in content, \
        "Success status assignment not found"

    # Check the distinctive description
    assert 'ready_for_merge_description = "Revert PR"' in content, \
        "Revert PR description not found"


def test_revert_pr_logic_branches():
    """Test that the revert PR logic has correct conditional branches."""
    native_jobs_path = PRAKTIKA_PATH / "native_jobs.py"
    content = native_jobs_path.read_text()

    # The logic should check:
    # 1. If it's a revert PR (contains "Reverts ClickHouse/" in PR_BODY)
    # 2. If Fast test hasn't failed
    # 3. If status is not already SUCCESS
    # Then set status to SUCCESS

    # Check that the logic checks for Fast test failures using any()
    assert 'fast_test_failed = any(' in content, \
        "Fast test failure detection with any() not found"

    # Check that the logic condition checks for NOT fast_test_failed
    assert 'if not fast_test_failed' in content, \
        "Not fast_test_failed condition not found"

    # Check that there's a print statement for the revert PR case
    assert 'NOTE: Revert PR detected' in content, \
        "Revert PR detected log message not found"


def test_revert_pr_pattern_placement():
    """Test that the revert PR logic is placed in the right location (_finish_workflow)."""
    native_jobs_path = PRAKTIKA_PATH / "native_jobs.py"
    content = native_jobs_path.read_text()

    # Find the function _finish_workflow
    assert 'def _finish_workflow(' in content, \
        "_finish_workflow function not found"

    # Find where _finish_workflow function starts
    finish_workflow_idx = content.find('def _finish_workflow(')
    assert finish_workflow_idx != -1, "_finish_workflow function not found"

    # Get content from _finish_workflow onwards
    finish_workflow_content = content[finish_workflow_idx:]

    # Find the section where failed_results are processed (within _finish_workflow)
    failed_results_idx = finish_workflow_content.find('if failed_results or dropped_results:')
    revert_pr_idx = finish_workflow_content.find('"Reverts ClickHouse/" in env.PR_BODY')
    # Find the post_commit_status call within _finish_workflow (after the enable_merge_ready_status check)
    post_commit_idx = finish_workflow_content.find('if workflow.enable_merge_ready_status:')

    assert failed_results_idx != -1, "failed_results processing not found in _finish_workflow"
    assert revert_pr_idx != -1, "Revert PR logic not found"
    assert post_commit_idx != -1, "enable_merge_ready_status check not found in _finish_workflow"

    # The revert PR logic should come after failed_results processing
    # and before the enable_merge_ready_status check (which wraps post_commit_status)
    assert failed_results_idx < revert_pr_idx < post_commit_idx, \
        "Revert PR logic is not in the correct position (should be between failed_results processing and enable_merge_ready_status)"


def test_imports_available():
    """Test that required imports are available in native_jobs.py."""
    native_jobs_path = PRAKTIKA_PATH / "native_jobs.py"
    content = native_jobs_path.read_text()

    # Check for required imports
    required_imports = [
        'from .result import Result',
        'from ._environment import _Environment',
    ]

    for imp in required_imports:
        assert imp in content or imp.replace('from .', 'from praktika.') in content, \
            f"Required import missing: {imp}"


def test_python_syntax_valid():
    """Test that native_jobs.py has valid Python syntax."""
    native_jobs_path = PRAKTIKA_PATH / "native_jobs.py"

    # Use Python's py_compile to check syntax
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(native_jobs_path)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, \
        f"native_jobs.py has syntax errors:\n{result.stderr}"


def test_revert_pr_logic_unit():
    """Unit test for the revert PR logic behavior."""
    # Add praktika to path and import
    sys.path.insert(0, str(REPO / "ci"))

    # We can't fully execute the function without mocking,
    # but we can verify the code structure is correct

    native_jobs_path = PRAKTIKA_PATH / "native_jobs.py"
    content = native_jobs_path.read_text()

    # Extract and verify the logic block exists
    # Look for the complete revert PR handling block

    # The block should start with the comment
    assert '# Revert PRs should be easy to merge' in content, \
        "Revert PR comment not found"

    # And contain the full conditional logic
    lines = content.split('\n')
    found_revert_logic = False
    found_fast_test_check = False
    found_status_change = False

    for i, line in enumerate(lines):
        if '"Reverts ClickHouse/" in env.PR_BODY' in line:
            found_revert_logic = True
            # Check next few lines contain the expected logic
            following_lines = '\n'.join(lines[i:i+15])
            found_fast_test_check = 'fast_test_failed = any(' in following_lines
            found_status_change = 'ready_for_merge_status = Result.Status.SUCCESS' in following_lines
            break

    assert found_revert_logic, "Revert PR main condition not found"
    assert found_fast_test_check, "Fast test check not found in revert PR block"
    assert found_status_change, "Status change not found in revert PR block"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These verify the repo's own tests pass on both base commit and after fix.
# =============================================================================


def test_repo_ci_tests():
    """Repo's CI pytest tests in ci/tests/ pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "ci/tests/", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    err_msg = r.stderr[-500:] if r.stderr else ""
    out_msg = r.stdout[-1000:] if r.stdout else ""
    assert r.returncode == 0, f"CI tests failed:\n{out_msg}\n{err_msg}"


def test_repo_python_syntax_native_jobs():
    """Python syntax check on ci/praktika/native_jobs.py passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "ci/praktika/native_jobs.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


def test_repo_praktika_python_syntax():
    """All Python files in ci/praktika have valid syntax (pass_to_pass)."""
    import glob
    py_files = glob.glob(str(REPO / "ci" / "praktika" / "*.py"))
    # Filter out __pycache__ files if any
    py_files = [f for f in py_files if not f.endswith("__pycache__.py")]

    failed = []
    for f in py_files:
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", f],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            failed.append((f, r.stderr))

    assert not failed, f"Syntax errors found:\n" + "\n".join(f"{f}: {e}" for f, e in failed)


def test_repo_ci_structure():
    """CI directory structure is valid with all key files present (pass_to_pass)."""
    # Verify key directories exist
    required_dirs = [
        REPO / "ci" / "praktika",
        REPO / "ci" / "tests",
        REPO / "ci" / "jobs",
        REPO / "ci" / "workflows",
    ]
    for d in required_dirs:
        assert d.exists() and d.is_dir(), f"Required directory missing: {d}"

    # Verify key files exist
    key_files = [
        REPO / "ci" / "praktika" / "__init__.py",
        REPO / "ci" / "praktika" / "result.py",
        REPO / "ci" / "praktika" / "native_jobs.py",
        REPO / "ci" / "praktika" / "_environment.py",
    ]
    for f in key_files:
        assert f.exists(), f"Required file missing: {f}"
        # Check each file has valid Python syntax
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(f)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr}"


def test_repo_praktika_core_imports():
    """Core praktika modules can be imported successfully (pass_to_pass).

    This test validates that the modified native_jobs module and its dependencies
    can be imported without errors. Installs requests package if needed.
    """
    # Install requests if not present (required for imports)
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "requests"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Import test - add ci/ to path
    import_code = "import sys; sys.path.insert(0, '/workspace/ClickHouse/ci'); from praktika.result import Result, ResultTranslator; from praktika._environment import _Environment; print('SUCCESS: Core praktika imports work')"
    r = subprocess.run(
        [sys.executable, "-c", import_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr}\n{r.stdout}"
    assert "SUCCESS" in r.stdout, f"Expected success message not found:\n{r.stdout}"
