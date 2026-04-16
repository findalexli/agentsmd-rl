"""
Tests for apache/airflow#64737: Fix duplicate deadline callbacks with HA scheduler replicas.

The fix wraps the deadline query with with_row_locks(..., skip_locked=True, key_share=False)
to prevent concurrent HA scheduler replicas from processing the same deadline row.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/airflow")
SCHEDULER_FILE = REPO / "airflow-core/src/airflow/jobs/scheduler_job_runner.py"


def get_deadline_handling_code():
    """Extract the section of code that handles deadline processing."""
    content = SCHEDULER_FILE.read_text()

    # Find the section that queries Deadline model
    # Look for code that selects from Deadline and calls handle_miss
    lines = content.split('\n')

    deadline_section_start = None
    deadline_section_end = None

    for i, line in enumerate(lines):
        # Find where Deadline query starts
        if 'select(Deadline)' in line or 'Deadline.deadline_time' in line:
            # Go back a few lines to capture the full context
            deadline_section_start = max(0, i - 10)
        if deadline_section_start is not None and 'handle_miss' in line:
            deadline_section_end = i + 5
            break

    if deadline_section_start is not None and deadline_section_end is not None:
        return '\n'.join(lines[deadline_section_start:deadline_section_end])

    # Return the full content if we can't find the specific section
    return content


def test_scheduler_file_syntax():
    """Scheduler module has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SCHEDULER_FILE)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Syntax error in scheduler_job_runner.py:\n{result.stderr}"


def test_deadline_query_uses_row_locks():
    """Deadline query is wrapped with with_row_locks (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # The fix should wrap the Deadline query with with_row_locks
    # Check that with_row_locks appears in proximity to the Deadline query
    has_row_locks_near_deadline = (
        'with_row_locks' in deadline_code and
        ('Deadline' in deadline_code or 'deadline' in deadline_code.lower())
    )

    assert has_row_locks_near_deadline, (
        "The Deadline query must be wrapped with with_row_locks() to prevent "
        "duplicate processing by concurrent HA scheduler replicas. "
        "Found deadline code section but no with_row_locks call nearby."
    )


def test_deadline_row_locks_skip_locked():
    """Deadline query's with_row_locks uses skip_locked=True (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # Must have skip_locked=True near the Deadline query
    has_skip_locked = 'skip_locked=True' in deadline_code or 'skip_locked = True' in deadline_code

    assert has_skip_locked, (
        "The Deadline query's with_row_locks must use skip_locked=True to allow "
        "concurrent schedulers to skip already-locked rows instead of waiting"
    )


def test_deadline_row_locks_key_share_false():
    """Deadline query's with_row_locks uses key_share=False (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # Must have key_share=False near the Deadline query
    has_key_share_false = 'key_share=False' in deadline_code or 'key_share = False' in deadline_code

    assert has_key_share_false, (
        "The Deadline query's with_row_locks must use key_share=False because "
        "FOR KEY SHARE lock mode does not conflict with itself, which would "
        "still allow duplicate processing"
    )


def test_deadline_row_locks_specifies_model():
    """Deadline query's with_row_locks specifies of=Deadline (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # Must specify of=Deadline to target the correct table
    has_of_deadline = 'of=Deadline' in deadline_code or 'of = Deadline' in deadline_code

    assert has_of_deadline, (
        "The Deadline query's with_row_locks must specify of=Deadline to "
        "explicitly target the Deadline model for row-level locking"
    )


def test_deadline_query_extracted_to_variable():
    """Deadline SELECT query is extracted into a variable (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # The fix extracts the query into a deadline_query variable
    # This is required because with_row_locks wraps the query
    has_deadline_query_var = 'deadline_query' in deadline_code

    assert has_deadline_query_var, (
        "The Deadline SELECT query should be extracted into a 'deadline_query' variable "
        "before being passed to with_row_locks for clarity and proper wrapping"
    )


def test_deadline_code_has_explanatory_comment():
    """Code includes comment explaining the row locking purpose (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # Look for a comment explaining the purpose of the locking
    # The comment should mention HA/concurrent schedulers and preventing duplicates
    deadline_code_lower = deadline_code.lower()

    has_ha_mention = 'ha ' in deadline_code_lower or 'high availability' in deadline_code_lower or 'concurrent' in deadline_code_lower or 'replicas' in deadline_code_lower
    has_duplicate_mention = 'duplicate' in deadline_code_lower or 'skip' in deadline_code_lower
    has_lock_mention = 'lock' in deadline_code_lower or 'for update' in deadline_code_lower

    # Must have at least a comment about the locking purpose
    has_explanatory_comment = has_lock_mention and (has_ha_mention or has_duplicate_mention)

    assert has_explanatory_comment, (
        "The deadline locking code should include a comment explaining why row locking "
        "is needed (to prevent duplicate callbacks in HA deployments with concurrent schedulers)"
    )


def test_deadline_session_passed_to_row_locks():
    """with_row_locks for deadline query receives session parameter (fail_to_pass)."""
    deadline_code = get_deadline_handling_code()

    # The with_row_locks call must receive a session parameter
    # Check for session= in proximity to with_row_locks
    if 'with_row_locks' not in deadline_code:
        # If no with_row_locks, this test should fail
        assert False, "No with_row_locks found in deadline handling code"

    # Look for session parameter in the with_row_locks call
    has_session = 'session=session' in deadline_code or 'session = session' in deadline_code

    assert has_session, (
        "The deadline query's with_row_locks must receive a session parameter "
        "to determine the database dialect for appropriate locking behavior"
    )


def test_deadline_query_not_inline():
    """Deadline query is not inline in session.scalars (fail_to_pass)."""
    content = SCHEDULER_FILE.read_text()

    # The buggy pattern is: session.scalars(select(Deadline)...) without row locks
    # The fix pattern is: session.scalars(with_row_locks(deadline_query, ...))

    # Look for the problematic inline pattern near Deadline
    buggy_pattern = re.search(
        r'for\s+deadline\s+in\s+session\.scalars\s*\(\s*\n?\s*select\s*\(\s*Deadline\s*\)',
        content,
        re.MULTILINE | re.DOTALL
    )

    # This pattern should NOT exist in the fixed code
    assert buggy_pattern is None, (
        "The Deadline query should not be inline in session.scalars(). "
        "It must be wrapped with with_row_locks() to prevent race conditions "
        "in HA scheduler deployments."
    )


def test_repo_ruff_lint_scheduler():
    """Repo's ruff linter passes on scheduler_job_runner.py (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(SCHEDULER_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed on scheduler file:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_lint_sqlalchemy_utils():
    """Repo's ruff linter passes on utils/sqlalchemy.py (pass_to_pass)."""
    sqlalchemy_file = REPO / "airflow-core/src/airflow/utils/sqlalchemy.py"
    # Install ruff if not available
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(sqlalchemy_file)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed on sqlalchemy utils:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_lint_jobs_module():
    """Repo's ruff linter passes on entire jobs module (pass_to_pass)."""
    jobs_dir = REPO / "airflow-core/src/airflow/jobs"
    # Install ruff if not available
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(jobs_dir)],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed on jobs module:\n{result.stdout}\n{result.stderr}"


# ── Coding Convention Tests (verifying rubric rules programmatically) ──

def test_no_assert_in_deadline_fix():
    """The deadline fix does not introduce assert statements (pass_to_pass)."""
    deadline_code = get_deadline_handling_code()
    # Check that no assert statements are added in the deadline handling section
    # (assert is stripped by python -O, so production code shouldn't use it)
    assert 'assert ' not in deadline_code or 'AssertionError' in deadline_code, (
        "Production code should not use assert statements - they are stripped by python -O"
    )


def test_no_session_commit_in_deadline_fix():
    """The deadline fix does not call session.commit() (pass_to_pass)."""
    deadline_code = get_deadline_handling_code()
    # Functions receiving session parameter should not call session.commit()
    # because the caller manages the session lifecycle
    assert 'session.commit()' not in deadline_code, (
        "Functions receiving session parameter must not call session.commit() - "
        "caller manages the session lifecycle"
    )


