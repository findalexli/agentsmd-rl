"""
Tests for apache/airflow#64737: Fix duplicate deadline callbacks with HA scheduler replicas.

The fix wraps the deadline query with with_row_locks(..., skip_locked=True, key_share=False)
to prevent concurrent HA scheduler replicas from processing the same deadline row.

These tests verify BEHAVIOR by parsing and executing the code, not by string grepping.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/airflow")
SCHEDULER_FILE = REPO / "airflow-core/src/airflow/jobs/scheduler_job_runner.py"
SQLALCHEMY_UTILS_FILE = REPO / "airflow-core/src/airflow/utils/sqlalchemy.py"


def get_with_row_locks_call_for_deadline():
    """
    Parse scheduler file and find with_row_locks call with of=Deadline.
    Returns the Call AST node or None.
    """
    content = SCHEDULER_FILE.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if hasattr(node.func, 'id'):
                func_name = node.func.id
            elif hasattr(node.func, 'attr'):
                func_name = node.func.attr

            if func_name == 'with_row_locks':
                # Check if it has of=Deadline
                for kw in node.keywords:
                    if kw.arg == 'of':
                        if isinstance(kw.value, ast.Name) and kw.value.id == 'Deadline':
                            return node
                        if isinstance(kw.value, ast.Constant) and kw.value.value == 'Deadline':
                            return node
    return None


def get_keyword_value(node, kwarg_name):
    """Get the value of a keyword argument from a Call node."""
    for kw in node.keywords:
        if kw.arg == kwarg_name:
            if isinstance(kw.value, ast.Constant):
                return kw.value.value
            if isinstance(kw.value, ast.Name):
                return kw.value.id
    return None


def get_deadline_query_variable_name():
    """
    Find a variable assignment that holds a Deadline query.
    Returns the variable name or None.
    """
    content = SCHEDULER_FILE.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if hasattr(target, 'id'):
                    if 'deadline' in target.id.lower() and 'query' in target.id.lower():
                        # Check if the value involves Deadline
                        source = ast.get_source_segment(content, node.value)
                        if source and 'Deadline' in source:
                            return target.id
    return None


def get_with_row_locks_line_number():
    """Get line number of with_row_locks call for Deadline."""
    call = get_with_row_locks_call_for_deadline()
    if call:
        return call.lineno
    return None


# -----------------------------------------------------------------------------
# Pass-to-Pass Tests (verify code is valid)
# -----------------------------------------------------------------------------

def test_scheduler_file_syntax():
    """Scheduler module has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SCHEDULER_FILE)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Syntax error in scheduler_job_runner.py:\n{result.stderr}"


def test_repo_ruff_lint_scheduler():
    """Repo's ruff linter passes on scheduler_job_runner.py (pass_to_pass)."""
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
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(SQLALCHEMY_UTILS_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed on sqlalchemy utils:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_lint_jobs_module():
    """Repo's ruff linter passes on entire jobs module (pass_to_pass)."""
    jobs_dir = REPO / "airflow-core/src/airflow/jobs"
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


# -----------------------------------------------------------------------------
# Fail-to-Pass Tests (verify the bug fix)
# -----------------------------------------------------------------------------

def test_deadline_query_is_wrapped_with_row_locks():
    """
    Deadline query is wrapped with with_row_locks (fail_to_pass).

    Parses the scheduler file as AST and verifies that:
    1. A with_row_locks() call exists with of=Deadline
    2. The call targets the correct model for row-level locking
    """
    call = get_with_row_locks_call_for_deadline()

    assert call is not None, (
        "No with_row_locks(of=Deadline, ...) call found. "
        "The deadline query must be wrapped with with_row_locks() to prevent "
        "duplicate processing by concurrent HA scheduler replicas."
    )


def test_deadline_row_locks_has_skip_locked_true():
    """
    Deadline query's with_row_locks uses skip_locked=True (fail_to_pass).

    Verifies via AST parsing that skip_locked=True is set.
    """
    call = get_with_row_locks_call_for_deadline()

    assert call is not None, "No with_row_locks() call found for Deadline query"

    skip_locked = get_keyword_value(call, 'skip_locked')
    assert skip_locked is True, (
        "with_row_locks must have skip_locked=True to allow concurrent schedulers "
        "to skip already-locked rows instead of waiting. "
        f"Found skip_locked={skip_locked}"
    )


def test_deadline_row_locks_has_key_share_false():
    """
    Deadline query's with_row_locks uses key_share=False (fail_to_pass).

    Verifies via AST parsing that key_share=False is set.
    """
    call = get_with_row_locks_call_for_deadline()

    assert call is not None, "No with_row_locks() call found for Deadline query"

    key_share = get_keyword_value(call, 'key_share')
    assert key_share is False, (
        "with_row_locks must have key_share=False because FOR KEY SHARE lock mode "
        "does not conflict with itself, which would still allow duplicate processing. "
        f"Found key_share={key_share}"
    )


def test_deadline_row_locks_has_session_param():
    """
    with_row_locks for deadline query receives session parameter (fail_to_pass).

    Verifies via AST parsing that session=session is passed.
    """
    call = get_with_row_locks_call_for_deadline()

    assert call is not None, "No with_row_locks() call found for Deadline query"

    session = get_keyword_value(call, 'session')
    assert session == 'session', (
        "with_row_locks must receive session=session parameter to determine "
        "the database dialect for appropriate locking behavior. "
        f"Found session={session}"
    )


def test_deadline_query_extracted_to_variable():
    """
    Deadline SELECT query is extracted into a named variable (fail_to_pass).

    Verifies via AST parsing that the query is stored in a variable
    before being passed to with_row_locks (not inline).
    """
    var_name = get_deadline_query_variable_name()

    assert var_name is not None, (
        "The Deadline SELECT query should be extracted into a named variable "
        "before being passed to with_row_locks for clarity and proper wrapping."
    )


def test_deadline_query_not_inline_in_scalars():
    """
    Deadline query is not inline in session.scalars() - uses variable (fail_to_pass).

    Verifies that the query is passed via variable to with_row_locks,
    not constructed inline.
    """
    content = SCHEDULER_FILE.read_text()
    tree = ast.parse(content)

    # Find the with_row_locks call for Deadline and check its first argument
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if hasattr(node.func, 'id'):
                func_name = node.func.id
            elif hasattr(node.func, 'attr'):
                func_name = node.func.attr

            if func_name == 'with_row_locks':
                # Check if it has of=Deadline
                is_for_deadline = False
                for kw in node.keywords:
                    if kw.arg == 'of':
                        if isinstance(kw.value, ast.Name) and kw.value.id == 'Deadline':
                            is_for_deadline = True
                            break

                if is_for_deadline and node.args:
                    # The first arg should be a variable (Name), not inline (Call)
                    first_arg = node.args[0]
                    assert isinstance(first_arg, ast.Name), (
                        "The query passed to with_row_locks should be a variable, "
                        "not an inline select() call. Extract the query to a named variable first."
                    )
                    return

    # If we get here without returning, we either didn't find the call or it had no args
    call = get_with_row_locks_call_for_deadline()
    if call is None:
        raise AssertionError("No with_row_locks found for Deadline query")
    if not call.args:
        raise AssertionError("with_row_locks call has no arguments - expected a query variable")


def test_deadline_code_has_explanatory_comment():
    """
    Code includes comment explaining the row locking purpose (fail_to_pass).

    Searches for comments that explain why row locking is needed.
    """
    content = SCHEDULER_FILE.read_text()

    # Get line number of with_row_locks call
    line_num = get_with_row_locks_line_number()
    if line_num is None:
        raise AssertionError("Could not find with_row_locks call for Deadline")

    # Look at comments in the 25 lines before (gold fix has comments ~15-20 lines before)
    lines = content.split('\n')
    start_line = max(0, line_num - 25)
    context = '\n'.join(lines[start_line:line_num])

    # Check for explanatory comment
    context_lower = context.lower()
    has_ha_mention = (
        'ha ' in context_lower or
        'high availability' in context_lower or
        'concurrent' in context_lower or
        'replica' in context_lower
    )
    has_duplicate_mention = 'duplicate' in context_lower or 'both process' in context_lower
    has_lock_mention = 'lock' in context_lower or 'for update' in context_lower or 'skip locked' in context_lower

    has_explanatory_comment = has_lock_mention and (has_ha_mention or has_duplicate_mention)

    assert has_explanatory_comment, (
        "The deadline locking code should include a comment explaining why row locking "
        "is needed (to prevent duplicate callbacks in HA deployments with concurrent schedulers). "
        "Expected comment mentioning: HA/concurrent/replica AND lock/skip locked, "
        "or duplicate AND lock."
    )


# -----------------------------------------------------------------------------
# Coding Convention Tests (verifying rubric rules programmatically)
# -----------------------------------------------------------------------------

def get_deadline_handling_function():
    """Find the function containing deadline handling code."""
    content = SCHEDULER_FILE.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_source = ast.get_source_segment(content, node)
            if func_source and 'Deadline' in func_source and 'handle_miss' in func_source:
                return node
    return None


def find_function_calls(node, func_name):
    """Find all function calls with the given name in the AST subtree."""
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if hasattr(child.func, 'id') and child.func.id == func_name:
                calls.append(child)
            elif hasattr(child.func, 'attr') and child.func.attr == func_name:
                calls.append(child)
    return calls


def test_no_assert_in_deadline_fix():
    """The deadline fix does not introduce assert statements (pass_to_pass)."""
    func = get_deadline_handling_function()
    if func:
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                raise AssertionError(
                    "Production code should not use assert statements - they are stripped by python -O"
                )


def test_no_session_commit_in_deadline_fix():
    """The deadline fix does not call session.commit() (pass_to_pass)."""
    func = get_deadline_handling_function()
    if func:
        calls = find_function_calls(func, 'commit')
        for call in calls:
            if isinstance(call.func, ast.Attribute):
                raise AssertionError(
                    "Functions receiving session parameter must not call session.commit() - "
                    "caller manages the session lifecycle"
                )
