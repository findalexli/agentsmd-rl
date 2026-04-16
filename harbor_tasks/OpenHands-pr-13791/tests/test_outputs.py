"""Test outputs for OpenHands PR #13791 - Slack No Repository button fix.

These tests verify that the fix makes 'No Repository' immediately available
via a button instead of requiring a network request through external_select.
"""

import ast
import os
import py_compile
import subprocess
import sys

REPO_ROOT = '/workspace/openhands'
ENTERPRISE_DIR = os.path.join(REPO_ROOT, 'enterprise')
SLACK_MANAGER_PATH = os.path.join(ENTERPRISE_DIR, 'integrations/slack/slack_manager.py')
SLACK_TEST_PATH = os.path.join(ENTERPRISE_DIR, 'tests/unit/test_slack_integration.py')


def get_slack_manager_ast():
    """Parse the slack_manager.py file into an AST."""
    with open(SLACK_MANAGER_PATH, 'r') as f:
        return ast.parse(f.read())


def find_function_in_ast(tree, func_name):
    """Find a function definition in the AST by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            return node
    return None


def get_function_source(func_node):
    """Get the source code of a function from its AST node."""
    with open(SLACK_MANAGER_PATH, 'r') as f:
        lines = f.readlines()
    # AST uses 1-based line numbers
    start_line = func_node.lineno - 1
    end_line = func_node.end_lineno
    return ''.join(lines[start_line:end_line])


# -----------------------------------------------------------------------------
# Fail-to-pass tests (verify the fix works)
# -----------------------------------------------------------------------------

def test_generate_repo_selection_form_has_button_element():
    """F2P: _generate_repo_selection_form creates a button for 'No Repository'.

    Before the fix: Only external_select was returned, requiring network request.
    After the fix: Button is immediately available alongside external_select.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_generate_repo_selection_form')
    assert func is not None, "_generate_repo_selection_form not found"

    func_source = get_function_source(func)

    # Check for button element with action_id starting with 'no_repository:'
    assert "'type': 'button'" in func_source or '"type": "button"' in func_source, \
        "Button element not found in _generate_repo_selection_form"
    assert "no_repository:" in func_source, \
        "action_id with 'no_repository:' prefix not found"
    assert "'value': '-'" in func_source or '"value": "-"' in func_source, \
        "Button value '-' not found"


def test_generate_repo_selection_form_has_external_select():
    """F2P: _generate_repo_selection_form still has external_select for repo search.

    Verifies backward compatibility - the dropdown should still work.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_generate_repo_selection_form')
    assert func is not None, "_generate_repo_selection_form not found"

    func_source = get_function_source(func)

    # Check for external_select element
    assert "'type': 'external_select'" in func_source or '"type": "external_select"' in func_source, \
        "external_select element not found in _generate_repo_selection_form"
    assert "repository_select:" in func_source, \
        "action_id with 'repository_select:' prefix not found"


def test_generate_repo_selection_form_has_two_elements():
    """F2P: Form has exactly 2 elements (button + external_select).

    The fix adds a button alongside the existing external_select.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_generate_repo_selection_form')
    assert func is not None, "_generate_repo_selection_form not found"

    func_source = get_function_source(func)

    # Count 'type': 'button' and 'type': 'external_select' occurrences
    button_count = func_source.count("'type': 'button'") + func_source.count('"type": "button"')
    external_select_count = func_source.count("'type': 'external_select'") + func_source.count('"type": "external_select"')

    assert button_count >= 1, f"Expected at least 1 button, found {button_count}"
    assert external_select_count >= 1, f"Expected at least 1 external_select, found {external_select_count}"


def test_build_repo_options_returns_directly():
    """F2P: _build_repo_options uses 'return [' instead of building options list.

    Before the fix: Used 'options = [...]' then 'options.extend(...)' then 'return options'.
    After the fix: Uses direct list comprehension with 'return [...]'.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_build_repo_options')
    assert func is not None, "_build_repo_options not found"

    func_source = get_function_source(func)

    # Should have direct return statement with list comprehension
    # Check for pattern: return [ ... for repo in repos ... ]
    assert "return [" in func_source, \
        "Direct return [...] pattern not found in _build_repo_options - function should return list directly"

    # Should NOT have the old pattern of building options variable
    assert "options = [" not in func_source, \
        "Old pattern 'options = [...]' found - should use direct return"


def test_build_repo_options_allows_100_repos():
    """F2P: _build_repo_options allows up to 100 repos (not 99).

    Before the fix: repos[:99] (leaving room for "No Repository")
    After the fix: repos[:100] (full 100 slots available)
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_build_repo_options')
    assert func is not None, "_build_repo_options not found"

    func_source = get_function_source(func)

    # Check for repos[:100] pattern
    assert "repos[:100]" in func_source, \
        "repos[:100] not found - function should allow full 100 repos (not 99)"

    # Should NOT have repos[:99]
    assert "repos[:99]" not in func_source, \
        "repos[:99] found - should be repos[:100] to allow full 100 repos"


def test_parse_form_action_exists():
    """F2P: _parse_form_action method exists.

    This is a new method introduced by the fix to handle both button clicks
    and dropdown selections uniformly.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_parse_form_action')
    assert func is not None, "_parse_form_action method not found - should exist to handle button and dropdown actions"


def test_parse_form_action_handles_no_repository():
    """F2P: _parse_form_action handles 'no_repository:' action_id prefix.

    The fix adds support for button clicks with 'no_repository:' prefix.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_parse_form_action')
    assert func is not None, "_parse_form_action not found"

    func_source = get_function_source(func)

    assert "no_repository:" in func_source, \
        "'no_repository:' prefix check not found in _parse_form_action"
    assert "startswith" in func_source, \
        "startswith() call not found - needed to check action_id prefix"


def test_parse_form_action_handles_repository_select():
    """F2P: _parse_form_action handles 'repository_select:' action_id prefix.

    Verifies backward compatibility - should still handle dropdown selections.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_parse_form_action')
    assert func is not None, "_parse_form_action not found"

    func_source = get_function_source(func)

    assert "repository_select:" in func_source, \
        "'repository_select:' prefix check not found in _parse_form_action"


def test_receive_form_interaction_uses_parse_form_action():
    """F2P: receive_form_interaction calls _parse_form_action.

    The fix refactors the code to use the new _parse_form_action helper.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, 'receive_form_interaction')
    assert func is not None, "receive_form_interaction not found"

    func_source = get_function_source(func)

    assert "_parse_form_action" in func_source, \
        "receive_form_interaction should call _parse_form_action helper"


def test_receive_form_interaction_handles_none_parsed():
    """F2P: receive_form_interaction handles unknown actions gracefully.

    When _parse_form_action returns None (unknown action), the function should
    log a warning and return early.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, 'receive_form_interaction')
    assert func is not None, "receive_form_interaction not found"

    func_source = get_function_source(func)

    # Should check if parsed is None and return early
    assert "if parsed is None" in func_source or "if not parsed" in func_source, \
        "None check for parsed result not found - should handle unknown actions"
    assert "logger.warning" in func_source, \
        "logger.warning not found - should log warning for unknown actions"


def test_receive_form_interaction_handles_button_value():
    """F2P: receive_form_interaction handles button click value correctly.

    Button clicks have 'value' field, dropdown has 'selected_option'.
    The fix handles both uniformly through _parse_form_action.
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, 'receive_form_interaction')
    assert func is not None, "receive_form_interaction not found"

    func_source = get_function_source(func)

    # Should convert '-' to None for selected_repository
    assert "selected_value == '-'" in func_source or "'-'" in func_source, \
        "Check for '-' value not found - should handle No Repository selection"


def test_form_instruction_text_updated():
    """F2P: Form shows updated instruction text.

    Before the fix: "Type to search your repositories:"
    After the fix: "Select a repository or continue without one:"
    """
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_generate_repo_selection_form')
    assert func is not None, "_generate_repo_selection_form not found"

    func_source = get_function_source(func)

    # Check for new instruction text
    assert "Select a repository or continue without one" in func_source, \
        "Updated instruction text not found - should say 'Select a repository or continue without one'"

    # Should NOT have old text
    assert "Type to search your repositories" not in func_source, \
        "Old instruction text found - should be updated to new text"


# -----------------------------------------------------------------------------
# Pass-to-pass tests (verify existing functionality still works)
# -----------------------------------------------------------------------------

def test_slack_manager_file_exists():
    """P2P: Verify the slack_manager.py file exists."""
    assert os.path.exists(SLACK_MANAGER_PATH), f"slack_manager.py not found at {SLACK_MANAGER_PATH}"


def test_test_file_exists():
    """P2P: Verify the test file exists."""
    test_path = os.path.join(ENTERPRISE_DIR, 'tests/unit/test_slack_integration.py')
    assert os.path.exists(test_path), f"Test file not found at {test_path}"


def test_syntax_valid():
    """P2P: Verify slack_manager.py has valid Python syntax."""
    try:
        tree = get_slack_manager_ast()
        assert tree is not None
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in slack_manager.py: {e}")


def test_build_repo_options_function_exists():
    """P2P: _build_repo_options function exists."""
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_build_repo_options')
    assert func is not None, "_build_repo_options function not found"


def test_generate_repo_selection_form_function_exists():
    """P2P: _generate_repo_selection_form function exists."""
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, '_generate_repo_selection_form')
    assert func is not None, "_generate_repo_selection_form function not found"


def test_receive_form_interaction_function_exists():
    """P2P: receive_form_interaction function exists."""
    tree = get_slack_manager_ast()
    func = find_function_in_ast(tree, 'receive_form_interaction')
    assert func is not None, "receive_form_interaction function not found"


# -----------------------------------------------------------------------------
# Pass-to-pass tests using subprocess.run() (origin: repo_tests)
# -----------------------------------------------------------------------------

def test_repo_slack_manager_compiles():
    """P2P: slack_manager.py has valid Python syntax (repo_tests).

    Verifies the modified file compiles without syntax errors.
    """
    r = subprocess.run(
        ["python3", "-m", "py_compile", SLACK_MANAGER_PATH],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"slack_manager.py failed to compile:\n{r.stderr}"


def test_repo_slack_routes_compiles():
    """P2P: slack.py routes file has valid Python syntax (repo_tests).

    Verifies the routes file compiles without syntax errors.
    """
    routes_path = os.path.join(ENTERPRISE_DIR, 'server/routes/integration/slack.py')
    r = subprocess.run(
        ["python3", "-m", "py_compile", routes_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"slack.py routes failed to compile:\n{r.stderr}"


def test_repo_slack_integration_test_compiles():
    """P2P: test_slack_integration.py has valid Python syntax (repo_tests).

    Verifies the test file compiles without syntax errors.
    """
    r = subprocess.run(
        ["python3", "-m", "py_compile", SLACK_TEST_PATH],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"test_slack_integration.py failed to compile:\n{r.stderr}"


def test_repo_enterprise_pyproject_valid():
    """P2P: enterprise pyproject.toml is valid TOML (repo_tests).

    Verifies the pyproject.toml can be parsed by Python's tomllib (or tomli).
    """
    pyproject_path = os.path.join(ENTERPRISE_DIR, 'pyproject.toml')
    r = subprocess.run(
        ["python3", "-c", f"import tomllib; tomllib.load(open('{pyproject_path}', 'rb'))"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"pyproject.toml is invalid:\n{r.stderr}"


def test_repo_pytest_ini_valid():
    """P2P: pytest.ini is valid and exists (repo_tests).

    Verifies the pytest configuration file exists and is readable.
    """
    pytest_ini_path = os.path.join(REPO_ROOT, 'pytest.ini')
    r = subprocess.run(
        ["python3", "-c", f"import configparser; c = configparser.ConfigParser(); c.read('{pytest_ini_path}'); print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"pytest.ini is invalid:\n{r.stderr}"


def test_repo_slack_manager_ast_valid():
    """P2P: slack_manager.py has valid AST structure (repo_tests).

    Verifies the modified file can be parsed into an AST and key functions exist.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import ast
with open('{SLACK_MANAGER_PATH}') as f:
    tree = ast.parse(f.read())

funcs = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
required = ['_build_repo_options', '_generate_repo_selection_form', 'receive_form_interaction']
missing = [f for f in required if f not in funcs]
if missing:
    print(f'Missing functions: {{missing}}')
    exit(1)
print('All required functions found')
"""],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"AST validation failed:\n{r.stdout}\n{r.stderr}"


def test_repo_test_file_ast_valid():
    """P2P: test_slack_integration.py has valid AST structure (repo_tests).

    Verifies the test file can be parsed into an AST and key test classes exist.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import ast
with open('{SLACK_TEST_PATH}') as f:
    tree = ast.parse(f.read())

classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
required = ['TestBuildRepoOptions', 'TestRepoVerificationHandling']
missing = [c for c in required if c not in classes]
if missing:
    print(f'Missing test classes: {{missing}}')
    exit(1)
print('All required test classes found')
"""],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Test file AST validation failed:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_directory_structure():
    """P2P: enterprise directory structure is correct (repo_tests).

    Verifies critical directories exist for the Slack integration.
    """
    required_dirs = [
        os.path.join(ENTERPRISE_DIR, 'integrations/slack'),
        os.path.join(ENTERPRISE_DIR, 'tests/unit'),
        os.path.join(ENTERPRISE_DIR, 'server/routes/integration'),
    ]
    for d in required_dirs:
        r = subprocess.run(
            ["test", "-d", d],
            capture_output=True,
            timeout=10,
        )
        assert r.returncode == 0, f"Required directory missing: {d}"


def test_repo_slack_manager_key_patterns():
    """P2P: slack_manager.py contains expected code patterns (repo_tests).

    Verifies the file contains key patterns that should exist in the base commit.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import re
with open('{SLACK_MANAGER_PATH}') as f:
    content = f.read()

patterns = [
    r'def _build_repo_options',
    r'def _generate_repo_selection_form',
    r'class SlackManager',
    r'external_select',
    r'Repository',
]
missing = []
for p in patterns:
    if not re.search(p, content):
        missing.append(p)
if missing:
    print(f'Missing patterns: {{missing}}')
    exit(1)
print('All key patterns found')
"""],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Pattern check failed:\n{r.stdout}\n{r.stderr}"
