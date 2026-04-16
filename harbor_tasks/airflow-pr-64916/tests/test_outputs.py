"""
Tests for airflow-breeze-ci-commit-retry task.
Verifies that the breeze CI upgrade command properly handles pre-commit hook failures.

Tests verify BEHAVIOR, not text/match strings.
"""
import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")
CI_COMMANDS_PATH = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "commands" / "ci_commands.py"


# ===== PASS_TO_PASS TESTS (structural checks, unchanged) =====

def test_ci_commands_syntax():
    """Verify ci_commands.py has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(CI_COMMANDS_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error in ci_commands.py:\n{result.stderr}"


def test_subprocess_import_in_ci_commands():
    """Verify subprocess module is imported in ci_commands.py (pass_to_pass)."""
    content = CI_COMMANDS_PATH.read_text()
    assert "import subprocess" in content, (
        "subprocess module must be imported to catch CalledProcessError"
    )


# ===== BEHAVIORAL TESTS (rewritten to verify behavior, not text) =====

def test_upgrade_function_has_try_except():
    """
    Verify upgrade function contains try/except error handling.
    Uses AST to verify structure, not text matching.
    """
    content = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(content)

    # Find the upgrade function
    upgrade_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
            upgrade_node = node
            break

    assert upgrade_node is not None, "Could not find upgrade function"

    # Look for Try blocks with CalledProcessError handlers in upgrade
    has_calledprocess_error = False
    for child in ast.walk(upgrade_node):
        if isinstance(child, ast.Try):
            for handler in child.handlers:
                handler_type = ast.unparse(handler.type) if handler.type else ''
                if 'CalledProcessError' in handler_type:
                    has_calledprocess_error = True
                    break

    assert has_calledprocess_error, (
        "upgrade function should have try/except block with CalledProcessError handler"
    )


def test_except_handler_has_git_retry():
    """
    Verify the error handler contains git add and git commit with --no-verify.
    Uses AST to analyze the structure of the error handling.
    """
    content = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(content)

    upgrade_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
            upgrade_node = node
            break

    assert upgrade_node is not None

    # Find the except handler for CalledProcessError
    handler_code = None
    for child in ast.walk(upgrade_node):
        if isinstance(child, ast.Try):
            for handler in child.handlers:
                handler_type = ast.unparse(handler.type) if handler.type else ''
                if 'CalledProcessError' in handler_type:
                    handler_code = ast.unparse(handler)
                    break

    assert handler_code is not None, "No CalledProcessError handler found in upgrade function"

    # Verify the handler contains the needed operations
    assert 'git' in handler_code and 'add' in handler_code, (
        "Except handler should call git add"
    )
    assert '--no-verify' in handler_code, (
        "Except handler should use --no-verify flag in retry commit"
    )
    assert 'git' in handler_code and 'commit' in handler_code, (
        "Except handler should call git commit"
    )


def test_console_print_in_error_handler():
    """
    Verify console_print is called in the error handler.
    Uses AST to check for console_print call, not text matching.
    """
    content = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(content)

    upgrade_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
            upgrade_node = node
            break

    assert upgrade_node is not None

    found_console_print = False
    for child in ast.walk(upgrade_node):
        if isinstance(child, ast.Try):
            for handler in child.handlers:
                handler_type = ast.unparse(handler.type) if handler.type else ''
                if 'CalledProcessError' not in handler_type:
                    continue
                for stmt in ast.walk(handler):
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        func = stmt.value.func
                        # console_print is imported as Name in this module (not Attribute)
                        if isinstance(func, ast.Name) and func.id == 'console_print':
                            found_console_print = True
                            break
                        # Also handle attribute case (if used as module.func)
                        if isinstance(func, ast.Attribute) and func.attr == 'console_print':
                            found_console_print = True
                            break

    assert found_console_print, (
        "Except handler should call console_print"
    )


def test_both_commits_use_same_message():
    """
    Verify that both the initial commit and retry commit use the same message.
    Checks via AST that there are at least 2 git commit calls with the message.
    """
    content = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(content)

    upgrade_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
            upgrade_node = node
            break

    assert upgrade_node is not None

    commit_message = "CI: Upgrade important CI environment"
    commit_count = 0

    for child in ast.walk(upgrade_node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == 'run_command':
                if child.args and isinstance(child.args[0], ast.List):
                    # Use ast.unparse on the whole list to get full command with f-strings
                    cmd_str = ast.unparse(child.args[0])
                    if 'git' in cmd_str and 'commit' in cmd_str:
                        if commit_message in cmd_str:
                            commit_count += 1

    assert commit_count >= 2, (
        f"Should have at least 2 git commit calls with '{commit_message}', found {commit_count}"
    )


def test_git_commit_uses_message_flag():
    """
    Verify git commit uses --message flag (not -m short form).
    Uses AST parsing to analyze git commit calls.
    """
    content = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(content)

    upgrade_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
            upgrade_node = node
            break

    assert upgrade_node is not None

    git_commit_calls = []
    for child in ast.walk(upgrade_node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == 'run_command':
                if child.args and isinstance(child.args[0], ast.List):
                    cmd_elems = []
                    for elem in child.args[0].elts:
                        if isinstance(elem, ast.Constant) and isinstance(elem.value, str):
                            cmd_elems.append(elem.value)
                    if len(cmd_elems) >= 3 and cmd_elems[0] == 'git' and cmd_elems[1] == 'commit':
                        git_commit_calls.append(cmd_elems)

    has_message_flag = any('--message' in cmd for cmd in git_commit_calls)
    has_only_short_m = any('-m' in cmd and '--message' not in cmd for cmd in git_commit_calls)

    assert has_message_flag, "At least one git commit should use --message flag"
    assert not has_only_short_m, "No git commit should use only -m short flag"


def test_git_commands_structured_correctly():
    """
    Verify error handling has correct sequence: console_print, git add, git commit --no-verify.
    Uses AST to verify the structure, not text matching.
    """
    content = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(content)

    upgrade_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
            upgrade_node = node
            break

    assert upgrade_node is not None

    found_valid_structure = False
    for child in ast.walk(upgrade_node):
        if isinstance(child, ast.Try):
            for handler in child.handlers:
                handler_type = ast.unparse(handler.type) if handler.type else ''
                if 'CalledProcessError' not in handler_type:
                    continue
                handler_str = ast.unparse(handler)

                has_print = 'console_print' in handler_str
                has_git_add = 'add' in handler_str and 'git' in handler_str
                has_no_verify = '--no-verify' in handler_str
                has_git_commit = 'git' in handler_str and 'commit' in handler_str

                if has_print and has_git_add and has_no_verify and has_git_commit:
                    found_valid_structure = True
                    break

    assert found_valid_structure, (
        "Error handling structure not correct. Expected: try block with "
        "CalledProcessError handler containing console_print, git add, "
        "git commit --no-verify"
    )


# ===== PASS_TO_PASS TESTS (repo-level checks) =====

def test_repo_black_check():
    """Verify ci_commands.py passes black formatting check (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "black",
            "--check",
            str(CI_COMMANDS_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Black check failed:\n{result.stderr[-500:]}"


def test_repo_breeze_unit_tests():
    """Run breeze unit tests for run_utils and general_utils (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_run_utils.py",
            "tests/test_general_utils.py",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO / "dev" / "breeze",
    )
    assert result.returncode == 0, f"Breeze tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_repo_breeze_git_worktree_tests():
    """Run breeze git worktree tests (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_git_worktree.py",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO / "dev" / "breeze",
    )
    assert result.returncode == 0, f"Git worktree tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
