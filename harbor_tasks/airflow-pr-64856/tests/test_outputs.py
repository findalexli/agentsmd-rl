"""
Test suite for airflow-breeze-ci-upgrade-commit-retry task.

Tests that the CI upgrade command properly handles pre-commit hook failures
by catching CalledProcessError and retrying with --no-verify.
"""

import ast
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

REPO = Path("/workspace/airflow")
CI_COMMANDS_PATH = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "commands" / "ci_commands.py"


def test_syntax_valid():
    """Verify the modified file has valid Python syntax (pass_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in ci_commands.py: {e}")


def test_calledprocesserror_import_present():
    """Verify subprocess.CalledProcessError is available for catching (fail_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(source)

    # Find try/except blocks that catch CalledProcessError
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is not None:
                # Check for subprocess.CalledProcessError or CalledProcessError
                if isinstance(node.type, ast.Attribute):
                    if node.type.attr == "CalledProcessError":
                        return  # Found it
                elif isinstance(node.type, ast.Name):
                    if node.type.id == "CalledProcessError":
                        return  # Found it

    raise AssertionError(
        "No exception handler for CalledProcessError found. "
        "The code should catch subprocess.CalledProcessError when commit fails."
    )


def test_no_verify_flag_in_retry():
    """Verify --no-verify is used in the retry commit attempt (fail_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(source)

    # Find calls to run_command with --no-verify
    found_no_verify_in_commit = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if it's a call to run_command
            if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                # Check the first argument (should be a list)
                if node.args and isinstance(node.args[0], ast.List):
                    elements = []
                    for elt in node.args[0].elts:
                        if isinstance(elt, ast.Constant):
                            elements.append(elt.value)

                    # Check if this is a git commit with --no-verify
                    if "git" in elements and "commit" in elements and "--no-verify" in elements:
                        found_no_verify_in_commit = True
                        break

    assert found_no_verify_in_commit, (
        "No git commit command with --no-verify flag found. "
        "The retry logic should use --no-verify to skip pre-commit hooks."
    )


def test_retry_adds_files_before_commit():
    """Verify the retry logic calls git add before the retry commit (fail_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(source)

    # Find except handlers for CalledProcessError and check if they contain git add
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            # Check if this handles CalledProcessError
            is_cpe_handler = False
            if node.type is not None:
                if isinstance(node.type, ast.Attribute):
                    if node.type.attr == "CalledProcessError":
                        is_cpe_handler = True
                elif isinstance(node.type, ast.Name):
                    if node.type.id == "CalledProcessError":
                        is_cpe_handler = True

            if is_cpe_handler:
                # Check the handler body for git add
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        if isinstance(stmt.func, ast.Name) and stmt.func.id == "run_command":
                            if stmt.args and isinstance(stmt.args[0], ast.List):
                                elements = []
                                for elt in stmt.args[0].elts:
                                    if isinstance(elt, ast.Constant):
                                        elements.append(elt.value)

                                if "git" in elements and "add" in elements:
                                    return  # Found git add in the exception handler

    raise AssertionError(
        "No git add command found in the CalledProcessError handler. "
        "The retry logic should add auto-fixed files before retrying commit."
    )


def test_try_except_structure_around_commit():
    """Verify the commit is wrapped in try/except structure (fail_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(source)

    # Find try blocks that contain git commit
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            # Check if the try body contains a git commit call
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Name) and stmt.func.id == "run_command":
                        if stmt.args and isinstance(stmt.args[0], ast.List):
                            elements = []
                            for elt in stmt.args[0].elts:
                                if isinstance(elt, ast.Constant):
                                    elements.append(elt.value)

                            if "git" in elements and "commit" in elements:
                                # Verify there's an except handler
                                if node.handlers:
                                    return  # Found try/except around commit

    raise AssertionError(
        "Git commit command is not wrapped in a try/except block. "
        "The commit should be wrapped to catch CalledProcessError for retry logic."
    )


def test_commit_message_unchanged():
    """Verify the commit message format is preserved (pass_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()

    # Check that the expected commit message pattern exists
    assert "CI: Upgrade important CI environment" in source, (
        "Expected commit message pattern 'CI: Upgrade important CI environment' not found"
    )


def test_console_print_on_failure():
    """Verify informational message is printed when commit fails (fail_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(source)

    # Find except handlers for CalledProcessError and check for console_print
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            is_cpe_handler = False
            if node.type is not None:
                if isinstance(node.type, ast.Attribute):
                    if node.type.attr == "CalledProcessError":
                        is_cpe_handler = True
                elif isinstance(node.type, ast.Name):
                    if node.type.id == "CalledProcessError":
                        is_cpe_handler = True

            if is_cpe_handler:
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        if isinstance(stmt.func, ast.Name) and stmt.func.id == "console_print":
                            return  # Found console_print in exception handler

    raise AssertionError(
        "No console_print call found in CalledProcessError handler. "
        "The code should inform the user when commit fails and retry is attempted."
    )


def test_message_flag_format():
    """Verify --message is used instead of -m for git commit (fail_to_pass)."""
    source = CI_COMMANDS_PATH.read_text()
    tree = ast.parse(source)

    # Find all git commit calls and check flag format
    found_long_form = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                if node.args and isinstance(node.args[0], ast.List):
                    elements = []
                    for elt in node.args[0].elts:
                        if isinstance(elt, ast.Constant):
                            elements.append(elt.value)

                    if "git" in elements and "commit" in elements:
                        if "--message" in elements:
                            found_long_form = True

    assert found_long_form, (
        "Git commit should use --message (long form) instead of -m. "
        "This is the pattern used in the retry logic."
    )


def test_repo_syntax_all_commands():
    """Validate syntax of all breeze command files (pass_to_pass)."""
    # Run Python AST validation on all command files
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import ast
import sys
from pathlib import Path
commands_dir = Path('/workspace/airflow/dev/breeze/src/airflow_breeze/commands')
errors = []
for py_file in commands_dir.glob('*.py'):
    try:
        ast.parse(py_file.read_text())
    except SyntaxError as e:
        errors.append(f'{py_file.name}: line {e.lineno}: {e.msg}')
if errors:
    for e in errors:
        print(e, file=sys.stderr)
    sys.exit(1)
print(f'Validated {len(list(commands_dir.glob("*.py")))} command files')
""",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax validation failed:\n{r.stderr}"


def test_repo_compileall_breeze_commands():
    """Compile check all breeze command files with py_compile (pass_to_pass)."""
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "dev/breeze/src/airflow_breeze/commands",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


def test_repo_license_header():
    """Verify Apache License header in ci_commands.py (pass_to_pass)."""
    # Check license header using Python subprocess
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
from pathlib import Path
f = Path('/workspace/airflow/dev/breeze/src/airflow_breeze/commands/ci_commands.py')
content = f.read_text()
if 'Licensed to the Apache Software Foundation' not in content[:500]:
    print('Missing Apache License header', file=sys.stderr)
    sys.exit(1)
if 'http://www.apache.org/licenses/LICENSE-2.0' not in content[:1000]:
    print('Missing license URL', file=sys.stderr)
    sys.exit(1)
print('License header OK')
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"License check failed:\n{r.stderr}"


def test_repo_future_annotations_import():
    """Verify from __future__ import annotations is present (pass_to_pass)."""
    # Airflow repo standard: all Python files should use future annotations
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
from pathlib import Path
f = Path('/workspace/airflow/dev/breeze/src/airflow_breeze/commands/ci_commands.py')
content = f.read_text()
# Check early in file (should be after license, before other imports)
first_500_lines = '\\n'.join(content.split('\\n')[:50])
if 'from __future__ import annotations' not in first_500_lines:
    print('Missing future annotations import', file=sys.stderr)
    sys.exit(1)
print('Future annotations import OK')
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Future annotations check failed:\n{r.stderr}"
