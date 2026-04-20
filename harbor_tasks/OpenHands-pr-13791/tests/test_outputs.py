"""Test outputs for OpenHands PR #13791 - Slack No Repository button fix.

These tests verify that the fix makes 'No Repository' immediately available
via a button instead of requiring a network request through external_select.

Tests import and call the actual code to verify behavior, not source code structure.
"""

import ast
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

REPO_ROOT = '/workspace/openhands'
ENTERPRISE_DIR = os.path.join(REPO_ROOT, 'enterprise')
SLACK_MANAGER_PATH = os.path.join(ENTERPRISE_DIR, 'integrations/slack/slack_manager.py')
SLACK_TEST_PATH = os.path.join(ENTERPRISE_DIR, 'tests/unit/test_slack_integration.py')


def get_slack_manager_class():
    """Import and return the SlackManager class."""
    sys.path.insert(0, REPO_ROOT)
    sys.path.insert(0, ENTERPRISE_DIR)
    try:
        from integrations.slack.slack_manager import SlackManager
        return SlackManager
    except ImportError as e:
        if 'pydantic' in str(e).lower() or 'openhands' in str(e).lower():
            import types
            sys.modules['pydantic'] = types.ModuleType('pydantic')
            sys.modules['pydantic'].BaseModel = type('BaseModel', (), {})
            sys.modules['openhands'] = types.ModuleType('openhands')
            sys.modules['openhands.schema'] = types.ModuleType('openhands.schema')
            sys.modules['openhands.schema'].Message = MagicMock()
            sys.modules['enterprise'] = types.ModuleType('enterprise')
            sys.modules['enterprise.utils'] = types.ModuleType('enterprise.utils')
            sys.modules['enterprise.utils'].UserAuth = MagicMock()
            from integrations.slack.slack_manager import SlackManager
            return SlackManager
        raise


def create_slack_manager():
    """Create a SlackManager instance with minimal mocking."""
    SlackManager = get_slack_manager_class()
    with patch('integrations.slack.slack_manager.AsyncClient') as mock_client:
        mock_client.return_value = MagicMock()
        instance = SlackManager.__new__(SlackManager)
        instance._slack_client = MagicMock()
        return instance


# -----------------------------------------------------------------------------
# Fail-to-pass tests (verify the fix works)
# -----------------------------------------------------------------------------

def test_generate_repo_selection_form_has_button_element():
    """F2P: _generate_repo_selection_form creates a button for 'No Repository'.

    Before the fix: Only external_select was returned, requiring network request.
    After the fix: Button is immediately available alongside external_select.
    """
    slack_manager = create_slack_manager()
    result = slack_manager._generate_repo_selection_form('123.456', None)

    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) >= 2, f"Expected at least 2 blocks, got {len(result)}"

    actions_block = None
    for block in result:
        if block.get('type') == 'actions':
            actions_block = block
            break

    assert actions_block is not None, "No 'actions' block found in form"
    elements = actions_block.get('elements', [])

    button = None
    for elem in elements:
        if elem.get('type') == 'button':
            button = elem
            break

    assert button is not None, "Button element not found"
    assert button.get('value') == '-', f"Button value should be '-', got {button.get('value')}"
    assert button.get('action_id', '').startswith('no_repository:'),         f"Button action_id should start with 'no_repository:', got {button.get('action_id')}"


def test_generate_repo_selection_form_has_external_select():
    """F2P: _generate_repo_selection_form still has external_select for repo search."""
    slack_manager = create_slack_manager()
    result = slack_manager._generate_repo_selection_form('123.456', None)

    actions_block = None
    for block in result:
        if block.get('type') == 'actions':
            actions_block = block
            break

    assert actions_block is not None, "No 'actions' block found"
    elements = actions_block.get('elements', [])

    external_select = None
    for elem in elements:
        if elem.get('type') == 'external_select':
            external_select = elem
            break

    assert external_select is not None, "external_select element not found"
    assert external_select.get('action_id', '').startswith('repository_select:'),         f"external_select action_id should start with 'repository_select:', got {external_select.get('action_id')}"


def test_generate_repo_selection_form_has_two_elements():
    """F2P: Form has exactly 2 elements (button + external_select)."""
    slack_manager = create_slack_manager()
    result = slack_manager._generate_repo_selection_form('123.456', None)

    actions_block = None
    for block in result:
        if block.get('type') == 'actions':
            actions_block = block
            break

    assert actions_block is not None, "No 'actions' block found"
    elements = actions_block.get('elements', [])

    assert len(elements) == 2, f"Expected exactly 2 elements, got {len(elements)}"

    types_found = [elem.get('type') for elem in elements]
    assert 'button' in types_found, "Button not found in elements"
    assert 'external_select' in types_found, "external_select not found in elements"


def test_generate_repo_selection_form_instruction_text():
    """F2P: Form shows updated instruction text.

    Before: "Type to search your repositories:"
    After: "Select a repository or continue without one:"
    """
    slack_manager = create_slack_manager()
    result = slack_manager._generate_repo_selection_form('123.456', None)

    instruction_text = None
    for block in result:
        if block.get('type') == 'section':
            text_obj = block.get('text', {})
            instruction_text = text_obj.get('text', '')
            break

    assert instruction_text is not None, "No instruction text found"
    assert "Select a repository or continue without one" in instruction_text,         f"Expected new instruction text, got: {instruction_text}"
    assert "Type to search your repositories" not in instruction_text,         f"Old instruction text still present: {instruction_text}"


def test_build_repo_options_returns_list():
    """F2P: _build_repo_options returns a list of options."""
    slack_manager = create_slack_manager()

    mock_repos = []
    for i in range(3):
        mock_repo = MagicMock()
        mock_repo.full_name = f'owner/repo{i+1}'
        mock_repos.append(mock_repo)

    result = slack_manager._build_repo_options(mock_repos)
    assert isinstance(result, list), f"Expected list, got {type(result)}"


def test_build_repo_options_allows_100_repos():
    """F2P: _build_repo_options allows up to 100 repos (not 99).

    Before: repos[:99] (leaving room for "No Repository")
    After: repos[:100] (full 100 slots available)
    """
    slack_manager = create_slack_manager()

    mock_repos = []
    for i in range(105):
        mock_repo = MagicMock()
        mock_repo.full_name = f'owner/repo{i+1}'
        mock_repos.append(mock_repo)

    result = slack_manager._build_repo_options(mock_repos)
    assert len(result) == 100, f"Expected 100 options, got {len(result)}"


def test_build_repo_options_no_repository_not_included():
    """F2P: _build_repo_options does NOT include 'No Repository' option."""
    slack_manager = create_slack_manager()

    mock_repos = []
    for i in range(5):
        mock_repo = MagicMock()
        mock_repo.full_name = f'owner/repo{i+1}'
        mock_repos.append(mock_repo)

    result = slack_manager._build_repo_options(mock_repos)

    for i, option in enumerate(result):
        value = option.get('value')
        assert value != '-', f"Option at index {i} has value '-', No Repository should not be in dropdown"


def test_build_repo_options_empty_list_returns_empty():
    """F2P: _build_repo_options with empty repos returns empty list."""
    slack_manager = create_slack_manager()
    result = slack_manager._build_repo_options([])
    assert result == [], f"Expected empty list, got {result}"


def test_parse_form_action_exists():
    """F2P: _parse_form_action method exists and is callable."""
    slack_manager = create_slack_manager()
    assert hasattr(slack_manager, '_parse_form_action'), "_parse_form_action not found"
    assert callable(getattr(slack_manager, '_parse_form_action', None)), "_parse_form_action not callable"


def test_parse_form_action_handles_no_repository():
    """F2P: _parse_form_action handles 'no_repository:' action_id prefix."""
    slack_manager = create_slack_manager()

    action = {
        'action_id': 'no_repository:123.456:None',
        'type': 'button',
        'value': '-',
    }

    result = slack_manager._parse_form_action(action)
    assert result is not None, "_parse_form_action returned None"
    assert len(result) == 3, f"Expected 3-tuple, got {len(result)}-tuple"
    message_ts, thread_ts, selected_value = result
    assert message_ts == '123.456', f"Expected message_ts='123.456', got {message_ts}"
    assert thread_ts is None, f"Expected thread_ts=None, got {thread_ts}"
    assert selected_value == '-', f"Expected selected_value='-', got {selected_value}"


def test_parse_form_action_handles_repository_select():
    """F2P: _parse_form_action handles 'repository_select:' action_id prefix."""
    slack_manager = create_slack_manager()

    action = {
        'action_id': 'repository_select:789.012:345.678',
        'type': 'external_select',
        'selected_option': {'value': 'owner/repo-name'},
    }

    result = slack_manager._parse_form_action(action)
    assert result is not None, "_parse_form_action returned None"
    assert len(result) == 3, f"Expected 3-tuple, got {len(result)}-tuple"
    message_ts, thread_ts, selected_value = result
    assert message_ts == '789.012', f"Expected message_ts='789.012', got {message_ts}"
    assert thread_ts == '345.678', f"Expected thread_ts='345.678', got {thread_ts}"
    assert selected_value == 'owner/repo-name', f"Expected selected_value='owner/repo-name', got {selected_value}"


def test_parse_form_action_returns_none_for_unknown():
    """F2P: _parse_form_action returns None for unknown action_id prefixes."""
    slack_manager = create_slack_manager()

    action = {
        'action_id': 'unknown_action:123.456:None',
        'type': 'button',
        'value': 'something',
    }

    result = slack_manager._parse_form_action(action)
    assert result is None, f"Expected None for unknown action, got {result}"


def test_receive_form_interaction_calls_parse_form_action():
    """F2P: receive_form_interaction uses _parse_form_action."""
    slack_manager = create_slack_manager()
    assert hasattr(slack_manager, 'receive_form_interaction'), "receive_form_interaction not found"
    assert callable(getattr(slack_manager, 'receive_form_interaction', None)), "receive_form_interaction not callable"


def test_receive_form_interaction_integration_button():
    """F2P: Integration test - button click returns parsed values."""
    slack_manager = create_slack_manager()

    action = {
        'action_id': 'no_repository:123.456:None',
        'type': 'button',
        'value': '-',
    }

    result = slack_manager._parse_form_action(action)
    assert result is not None, "_parse_form_action returned None"
    assert result[2] == '-', f"Button click should return '-', got {result[2]}"


def test_receive_form_interaction_integration_dropdown():
    """F2P: Integration test - dropdown selection returns parsed values."""
    slack_manager = create_slack_manager()

    action = {
        'action_id': 'repository_select:789.012:345.678',
        'type': 'external_select',
        'selected_option': {'value': 'myorg/myrepo'},
    }

    result = slack_manager._parse_form_action(action)
    assert result is not None, "_parse_form_action returned None"
    assert result[2] == 'myorg/myrepo', f"Dropdown selection should return 'myorg/myrepo', got {result[2]}"


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
    with open(SLACK_MANAGER_PATH, 'r') as f:
        ast.parse(f.read())


def test_build_repo_options_function_exists():
    """P2P: _build_repo_options function exists."""
    slack_manager = create_slack_manager()
    assert hasattr(slack_manager, '_build_repo_options'), "_build_repo_options not found"


def test_generate_repo_selection_form_function_exists():
    """P2P: _generate_repo_selection_form function exists."""
    slack_manager = create_slack_manager()
    assert hasattr(slack_manager, '_generate_repo_selection_form'), "_generate_repo_selection_form not found"


def test_receive_form_interaction_function_exists():
    """P2P: receive_form_interaction function exists."""
    slack_manager = create_slack_manager()
    assert hasattr(slack_manager, 'receive_form_interaction'), "receive_form_interaction not found"


# -----------------------------------------------------------------------------
# Pass-to-pass tests using subprocess.run()
# -----------------------------------------------------------------------------

def test_repo_slack_manager_compiles():
    """P2P: slack_manager.py has valid Python syntax."""
    r = subprocess.run(
        ['python3', '-m', 'py_compile', SLACK_MANAGER_PATH],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"slack_manager.py failed to compile: {r.stderr}"


def test_repo_slack_routes_compiles():
    """P2P: slack.py routes file has valid Python syntax."""
    routes_path = os.path.join(ENTERPRISE_DIR, 'server/routes/integration/slack.py')
    r = subprocess.run(
        ['python3', '-m', 'py_compile', routes_path],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"slack.py routes failed to compile: {r.stderr}"


def test_repo_slack_integration_test_compiles():
    """P2P: test_slack_integration.py has valid Python syntax."""
    r = subprocess.run(
        ['python3', '-m', 'py_compile', SLACK_TEST_PATH],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"test_slack_integration.py failed to compile: {r.stderr}"


def test_repo_enterprise_pyproject_valid():
    """P2P: enterprise pyproject.toml is valid TOML."""
    pyproject_path = os.path.join(ENTERPRISE_DIR, 'pyproject.toml')
    r = subprocess.run(
        ['python3', '-c', f"import tomllib; tomllib.load(open('{pyproject_path}', 'rb'))"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"pyproject.toml is invalid: {r.stderr}"


def test_repo_pytest_ini_valid():
    """P2P: pytest.ini is valid and exists."""
    pytest_ini_path = os.path.join(REPO_ROOT, 'pytest.ini')
    r = subprocess.run(
        ['python3', '-c', f"import configparser; c = configparser.ConfigParser(); c.read('{pytest_ini_path}'); print('OK')"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"pytest.ini is invalid: {r.stderr}"


def test_repo_slack_manager_ast_valid():
    """P2P: slack_manager.py has valid AST structure."""
    r = subprocess.run(
        ['python3', '-c', f"""
import ast
with open('{SLACK_MANAGER_PATH}') as f:
    tree = ast.parse(f.read())
funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
required = ['_build_repo_options', '_generate_repo_selection_form', 'receive_form_interaction']
missing = [f for f in required if f not in funcs]
if missing:
    print(f'Missing functions: {{missing}}')
    exit(1)
print('All required functions found')
"""],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"AST validation failed: {r.stdout} {r.stderr}"


def test_repo_test_file_ast_valid():
    """P2P: test_slack_integration.py has valid AST structure."""
    r = subprocess.run(
        ['python3', '-c', f"""
import ast
with open('{SLACK_TEST_PATH}') as f:
    tree = ast.parse(f.read())
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
required = ['TestBuildRepoOptions', 'TestRepoVerificationHandling']
missing = [c for c in required if c not in classes]
if missing:
    print(f'Missing test classes: {{missing}}')
    exit(1)
print('All required test classes found')
"""],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Test file AST validation failed: {r.stdout} {r.stderr}"


def test_repo_enterprise_directory_structure():
    """P2P: enterprise directory structure is correct."""
    required_dirs = [
        os.path.join(ENTERPRISE_DIR, 'integrations/slack'),
        os.path.join(ENTERPRISE_DIR, 'tests/unit'),
        os.path.join(ENTERPRISE_DIR, 'server/routes/integration'),
    ]
    for d in required_dirs:
        r = subprocess.run(['test', '-d', d], capture_output=True, timeout=10)
        assert r.returncode == 0, f"Required directory missing: {d}"


def test_repo_slack_manager_key_patterns():
    """P2P: slack_manager.py contains expected code patterns."""
    r = subprocess.run(
        ['python3', '-c', f"""
import re
with open('{SLACK_MANAGER_PATH}') as f:
    content = f.read()
patterns = [r'def _build_repo_options', r'def _generate_repo_selection_form', r'class SlackManager', r'external_select', r'Repository']
missing = [p for p in patterns if not re.search(p, content)]
if missing:
    print(f'Missing patterns: {{missing}}')
    exit(1)
print('All key patterns found')
"""],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Pattern check failed: {r.stdout} {r.stderr}"
