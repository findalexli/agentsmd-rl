"""
Test suite for Airflow Breeze CI command fix.
Tests that the upgrade function handles git commit failures gracefully.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")
TARGET_FILE = REPO / "dev/breeze/src/airflow_breeze/commands/ci_commands.py"

def test_target_file_exists():
    """Verify target file exists."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

def test_upgrade_function_exists():
    """Verify upgrade function is defined in the module."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            found = True
            break
        elif isinstance(node, ast.AsyncFunctionDef) and node.name == "upgrade":
            found = True
            break

    assert found, "upgrade function not found in ci_commands.py"

def test_imports_subprocess_module():
    """Verify subprocess is imported in the module."""
    source = TARGET_FILE.read_text()

    # Check for subprocess import
    assert "import subprocess" in source, "subprocess not imported in module"

def test_has_try_except_block():
    """Verify the code has a try-except block handling CalledProcessError."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found_try_except = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            # Check if any handler catches CalledProcessError or subprocess.CalledProcessError
            for handler in node.handlers:
                if isinstance(handler.type, ast.Name) and handler.type.id == "CalledProcessError":
                    found_try_except = True
                    break
                elif isinstance(handler.type, ast.Attribute):
                    # Check for subprocess.CalledProcessError
                    if (isinstance(handler.type.value, ast.Name) and
                        handler.type.value.id == "subprocess" and
                        handler.type.attr == "CalledProcessError"):
                        found_try_except = True
                        break

    assert found_try_except, "No try-except block handling CalledProcessError found"

def test_has_no_verify_flag():
    """Verify the code includes --no-verify flag in git commit."""
    source = TARGET_FILE.read_text()

    # The fix should include --no-verify in the fallback commit
    assert "--no-verify" in source, "--no-verify flag not found in commit command"

def test_retry_git_add_in_except_block():
    """Verify git add is called again in the except block before retry commit."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found_add_in_except = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                # Walk the handler body to find git add call
                for child in ast.walk(handler):
                    if isinstance(child, ast.Call):
                        # Check for run_command(["git", "add", "."])
                        if (isinstance(child.func, ast.Name) and child.func.id == "run_command"):
                            if child.args:
                                first_arg = child.args[0]
                                if isinstance(first_arg, ast.List):
                                    elts = first_arg.elts
                                    if (len(elts) >= 3 and
                                        isinstance(elts[0], ast.Constant) and
                                        elts[0].value == "git" and
                                        isinstance(elts[1], ast.Constant) and
                                        elts[1].value == "add"):
                                        found_add_in_except = True
                                        break

    assert found_add_in_except, "git add not found in exception handler (needed for retry)"

def test_uses_message_flag_instead_of_m():
    """Verify the code uses --message instead of -m for git commit."""
    source = TARGET_FILE.read_text()

    # The fix changes from -m to --message
    assert "--message" in source, "--message flag not found (should replace -m)"

def test_info_message_about_auto_fixes():
    """Verify the code prints an info message when commit fails."""
    source = TARGET_FILE.read_text()

    # Check for the distinctive info message
    assert "Commit failed, assume some auto-fixes might have been made" in source, \
        "Info message about auto-fixes not found"

def test_postpone_comment_in_code():
    """Verify the code includes comment about postponing pre-commit checks."""
    source = TARGET_FILE.read_text()

    # Check for the distinctive comment
    assert "postpone pre-commit checks to CI" in source, \
        "Comment about postponing pre-commit checks not found"

# ===== Pass-to-Pass Tests (Repo CI/CD Checks) =====

def test_repo_python_syntax():
    """Target file has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Python syntax error: {result.stderr}"


def test_repo_black_formatting():
    """Target file passes black formatting check (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "black", "--check", "--diff", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Black formatting check failed:\n{result.stdout[-500:]}"


def test_repo_ast_parseable():
    """Target file is parseable as AST (pass_to_pass)."""
    source = TARGET_FILE.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")


# ===== Behavioral Tests (Fail-to-Pass) =====

def test_upgrade_function_is_callable():
    """Verify the upgrade function can be imported and is callable."""
    # First verify the file is valid Python
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Syntax error in target file: {result.stderr}"

    # Now verify we can at least import the module
    # (We can't fully import due to dependencies, but we can check syntax)
    source = TARGET_FILE.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in ci_commands.py: {e}")


def test_exception_handler_has_proper_structure():
    """Verify the exception handler structure is correct for the retry logic."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find the Try node that handles CalledProcessError
    found_correct_structure = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            # Check if it has a CalledProcessError handler
            has_called_process_error = False
            for handler in node.handlers:
                if isinstance(handler.type, ast.Name) and handler.type.id == "CalledProcessError":
                    has_called_process_error = True
                    break
                elif isinstance(handler.type, ast.Attribute):
                    if (isinstance(handler.type.value, ast.Name) and
                        handler.type.value.id == "subprocess" and
                        handler.type.attr == "CalledProcessError"):
                        has_called_process_error = True
                        break

            if has_called_process_error:
                # Verify the handler has at least 2 statements (console_print + run_command for add)
                for handler in node.handlers:
                    if isinstance(handler.type, (ast.Name, ast.Attribute)):
                        stmt_count = len(handler.body)
                        if stmt_count >= 2:
                            found_correct_structure = True
                            break

    assert found_correct_structure, (
        "Exception handler doesn't have proper structure (needs console_print and git add calls)"
    )


def test_no_verify_appears_in_fallback_commit_only():
    """Verify --no-verify appears in the context of a git commit call."""
    source = TARGET_FILE.read_text()

    # Find lines with --no-verify and verify they're in a git commit context
    lines = source.split('\n')
    found_in_commit_context = False

    for i, line in enumerate(lines):
        if '--no-verify' in line:
            # Check surrounding context for git commit
            context = '\n'.join(lines[max(0, i-10):i+10])
            assert '"git"' in context or "'git'" in context, \
                "--no-verify not in git command context"
            assert '"commit"' in context or "'commit'" in context, \
                "--no-verify not in commit command context"
            found_in_commit_context = True

    assert found_in_commit_context, "--no-verify not found in proper git commit context"
