"""Tests for the user git info endpoint benchmark task.

This tests that:
1. The new /git-info endpoint exists and returns UserGitInfo
2. The old /info endpoint is deprecated
3. User model is an alias for UserGitInfo (backwards compatibility)
4. get_user_git_info method is implemented across user context classes

Behavioral tests execute actual code to verify runtime behavior.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path('/workspace/openhands')


def _run_python_code(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        [sys.executable, '-c', code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# ============================================================================
# FAIL-TO-PASS TESTS - These test the actual behavioral changes from the PR
# ============================================================================


def test_user_git_info_model_importable():
    """UserGitInfo model can be imported and instantiated (fail_to_pass)."""
    code = """
from openhands.integrations.service_types import UserGitInfo
# Verify it's a Pydantic model with the expected fields
user = UserGitInfo(
    id='123',
    login='testuser',
    avatar_url='https://example.com/avatar.png',
    company='TestCo',
    name='Test User',
    email='test@example.com'
)
print(f"id={user.id}, login={user.login}, avatar_url={user.avatar_url}")
assert user.id == '123'
assert user.login == 'testuser'
assert user.avatar_url == 'https://example.com/avatar.png'
assert user.company == 'TestCo'
assert user.name == 'Test User'
assert user.email == 'test@example.com'
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"UserGitInfo import/instantiation failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout, f"Test assertions failed: {r.stdout}"


def test_user_git_info_optional_fields():
    """UserGitInfo optional fields default to None (fail_to_pass)."""
    code = """
from openhands.integrations.service_types import UserGitInfo
# Create with only required fields
user = UserGitInfo(
    id='456',
    login='minimaluser',
    avatar_url='https://example.com/avatar.png'
)
# Optional fields should be None
assert user.company is None, f"company should be None, got {user.company}"
assert user.name is None, f"name should be None, got {user.name}"
assert user.email is None, f"email should be None, got {user.email}"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Optional fields test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_user_alias_works():
    """User alias works as an alias for UserGitInfo (fail_to_pass)."""
    code = """
from openhands.integrations.service_types import User, UserGitInfo
# Verify they are the same class
assert User is UserGitInfo, f"User is not UserGitInfo: {User} vs {UserGitInfo}"
# Verify we can instantiate through the alias
user = User(id='789', login='aliasuser', avatar_url='https://example.com/alias.png')
assert isinstance(user, UserGitInfo), "User instance should be instance of UserGitInfo"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"User alias test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_user_git_info_serializable():
    """UserGitInfo serializes to JSON correctly (fail_to_pass)."""
    code = """
import json
from openhands.integrations.service_types import UserGitInfo
user = UserGitInfo(
    id='123',
    login='testuser',
    avatar_url='https://example.com/avatar.png',
    company='TestCo',
    name='Test User',
    email='test@example.com'
)
# Test model_dump_json
json_str = user.model_dump_json()
data = json.loads(json_str)
assert data['id'] == '123'
assert data['login'] == 'testuser'
assert data['avatar_url'] == 'https://example.com/avatar.png'
assert data['company'] == 'TestCo'
assert data['name'] == 'Test User'
assert data['email'] == 'test@example.com'
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Serialization test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_new_git_info_endpoint_importable():
    """New /git-info endpoint function can be imported (fail_to_pass)."""
    code = """
from openhands.app_server.user.user_router import get_current_user_git_info
import inspect
# Verify it's an async function
assert inspect.iscoroutinefunction(get_current_user_git_info), \
    "get_current_user_git_info should be async"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Endpoint import test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_user_context_has_get_user_git_info_abstract():
    """UserContext defines abstract get_user_git_info method (fail_to_pass)."""
    code = """
import inspect
from abc import abstractmethod
from openhands.app_server.user.user_context import UserContext
# Check method exists
assert hasattr(UserContext, 'get_user_git_info'), \
    "UserContext should have get_user_git_info method"
# Check it's abstract by looking at the method's attributes
method = getattr(UserContext, 'get_user_git_info')
# An abstract method has __isabstractmethod__ set to True
assert getattr(method, '__isabstractmethod__', False), \
    "get_user_git_info should be decorated with @abstractmethod"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"UserContext abstract method test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_specify_user_context_has_get_user_git_info():
    """SpecifyUserContext has get_user_git_info abstract method (fail_to_pass)."""
    code = """
from openhands.app_server.user.specifiy_user_context import SpecifyUserContext
assert hasattr(SpecifyUserContext, 'get_user_git_info'), \
    "SpecifyUserContext should have get_user_git_info method"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"SpecifyUserContext test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_auth_user_context_implements_get_user_git_info():
    """AuthUserContext implements get_user_git_info method (fail_to_pass)."""
    code = """
import inspect
from openhands.app_server.user.auth_user_context import AuthUserContext
# Verify method exists and is async
assert hasattr(AuthUserContext, 'get_user_git_info'), \
    "AuthUserContext should have get_user_git_info method"
assert inspect.iscoroutinefunction(AuthUserContext.get_user_git_info), \
    "get_user_git_info should be async"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"AuthUserContext implementation test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_user_auth_has_get_user_git_info():
    """UserAuth base class implements get_user_git_info (fail_to_pass)."""
    code = """
import inspect
from openhands.server.user_auth.user_auth import UserAuth
# Verify method exists and is async
assert hasattr(UserAuth, 'get_user_git_info'), \
    "UserAuth should have get_user_git_info method"
assert inspect.iscoroutinefunction(UserAuth.get_user_git_info), \
    "get_user_git_info should be async"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"UserAuth implementation test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_endpoint_returns_user_git_info_type():
    """New endpoint has correct return type annotation (fail_to_pass)."""
    code = """
import inspect
from openhands.app_server.user.user_router import get_current_user_git_info
# Check the return type annotation
sig = inspect.signature(get_current_user_git_info)
return_annotation = sig.return_annotation
# Should be UserGitInfo
from openhands.integrations.service_types import UserGitInfo
assert return_annotation is UserGitInfo, \
    f"Return type should be UserGitInfo, got {return_annotation}"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Return type test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_old_endpoint_has_deprecated_flag():
    """Old /info endpoint is marked deprecated in FastAPI router (fail_to_pass)."""
    code = """
from openhands.server.routes.git import app as git_app
from openhands.server.routes.git import get_user
import inspect
# Check the function has deprecated=True in the route decorator
# We can check by examining the endpoint in the app routes
found_deprecated = False
for route in git_app.routes:
    if hasattr(route, 'path') and route.path in ['/info', '/api/user/info']:
        if hasattr(route, 'deprecated') and route.deprecated:
            found_deprecated = True
            break
assert found_deprecated, "Old /info endpoint should be marked deprecated=True"
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Deprecated flag test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_new_endpoint_raises_401_when_not_authenticated():
    """New endpoint raises 401 when get_user_git_info returns None (fail_to_pass)."""
    code = """
import asyncio
from unittest.mock import AsyncMock
from fastapi import HTTPException
from openhands.app_server.user.user_router import get_current_user_git_info

async def test_401():
    mock_context = AsyncMock()
    mock_context.get_user_git_info.return_value = None
    try:
        await get_current_user_git_info(user_context=mock_context)
        return False, "Should have raised HTTPException"
    except HTTPException as e:
        if e.status_code == 401 and 'Not authenticated' in str(e.detail):
            return True, "Correct 401 raised"
        return False, f"Wrong exception: {e.status_code} - {e.detail}"

result, msg = asyncio.run(test_401())
assert result, msg
print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"401 test failed: {r.stderr}\n{r.stdout}"
    assert 'PASS' in r.stdout


def test_service_types_compiles():
    """service_types.py compiles without syntax errors (fail_to_pass)."""
    r = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(REPO / 'openhands' / 'integrations' / 'service_types.py')],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"service_types.py syntax error: {r.stderr}"


def test_user_router_compiles():
    """user_router.py compiles without syntax errors (fail_to_pass)."""
    r = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(REPO / 'openhands' / 'app_server' / 'user' / 'user_router.py')],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"user_router.py syntax error: {r.stderr}"


# ============================================================================
# PASS-TO-PASS TESTS - These verify repo integrity
# ============================================================================


def test_service_types_file_valid():
    """service_types.py is syntactically valid Python (pass_to_pass)."""
    service_types_file = REPO / 'openhands' / 'integrations' / 'service_types.py'
    content = service_types_file.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"service_types.py has syntax error: {e}")


def test_user_router_file_valid():
    """user_router.py is syntactically valid Python (pass_to_pass)."""
    router_file = REPO / 'openhands' / 'app_server' / 'user' / 'user_router.py'
    content = router_file.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"user_router.py has syntax error: {e}")


def test_user_context_file_valid():
    """user_context.py is syntactically valid Python (pass_to_pass)."""
    file_path = REPO / 'openhands' / 'app_server' / 'user' / 'user_context.py'
    content = file_path.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"user_context.py has syntax error: {e}")


def test_auth_user_context_file_valid():
    """auth_user_context.py is syntactically valid Python (pass_to_pass)."""
    file_path = REPO / 'openhands' / 'app_server' / 'user' / 'auth_user_context.py'
    content = file_path.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"auth_user_context.py has syntax error: {e}")


def test_specify_user_context_file_valid():
    """specifiy_user_context.py is syntactically valid Python (pass_to_pass)."""
    file_path = REPO / 'openhands' / 'app_server' / 'user' / 'specifiy_user_context.py'
    content = file_path.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"specifiy_user_context.py has syntax error: {e}")


def test_user_auth_file_valid():
    """user_auth.py is syntactically valid Python (pass_to_pass)."""
    file_path = REPO / 'openhands' / 'server' / 'user_auth' / 'user_auth.py'
    content = file_path.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"user_auth.py has syntax error: {e}")


def test_git_routes_file_valid():
    """git.py routes file is syntactically valid Python (pass_to_pass)."""
    file_path = REPO / 'openhands' / 'server' / 'routes' / 'git.py'
    content = file_path.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"git.py has syntax error: {e}")


# ============================================================================
# REPO CI TESTS - Run actual linting/type checking on modified files
# ============================================================================


def test_repo_ruff_check_service_types():
    """Ruff lint check passes on service_types.py (pass_to_pass)."""
    install = subprocess.run([sys.executable, '-m', 'pip', 'install', 'ruff', '-q'],
                             capture_output=True, timeout=60)
    if install.returncode != 0:
        pytest.skip(f"Could not install ruff: {install.stderr}")
    r = subprocess.run(
        ['ruff', 'check', '--config', f'{REPO}/dev_config/python/ruff.toml', f'{REPO}/openhands/integrations/service_types.py'],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed on service_types.py:\n{r.stderr}"


def test_repo_ruff_format_check():
    """Ruff format check passes on modified files (pass_to_pass)."""
    install = subprocess.run([sys.executable, '-m', 'pip', 'install', 'ruff', '-q'],
                             capture_output=True, timeout=60)
    if install.returncode != 0:
        pytest.skip(f"Could not install ruff: {install.stderr}")
    r = subprocess.run(
        ['ruff', 'format', '--config', f'{REPO}/dev_config/python/ruff.toml', '--check',
         f'{REPO}/openhands/integrations/service_types.py',
         f'{REPO}/openhands/app_server/user/user_router.py',
         f'{REPO}/openhands/app_server/user/user_context.py',
         f'{REPO}/openhands/app_server/user/auth_user_context.py'],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}"


def test_repo_mypy_service_types():
    """MyPy type check passes on service_types.py (pass_to_pass)."""
    install = subprocess.run([sys.executable, '-m', 'pip', 'install', 'mypy', '-q'],
                             capture_output=True, timeout=60)
    if install.returncode != 0:
        pytest.skip(f"Could not install mypy: {install.stderr}")
    r = subprocess.run(
        ['mypy', '--config-file', f'{REPO}/dev_config/python/mypy.ini', f'{REPO}/openhands/integrations/service_types.py'],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"MyPy check failed on service_types.py:\n{r.stdout}\n{r.stderr}"


def test_repo_mypy_user_router():
    """MyPy type check passes on user_router.py (pass_to_pass)."""
    install = subprocess.run([sys.executable, '-m', 'pip', 'install', 'mypy', '-q'],
                             capture_output=True, timeout=60)
    if install.returncode != 0:
        pytest.skip(f"Could not install mypy: {install.stderr}")
    r = subprocess.run(
        ['mypy', '--config-file', f'{REPO}/dev_config/python/mypy.ini', f'{REPO}/openhands/app_server/user/user_router.py'],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"MyPy check failed on user_router.py:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax_compile():
    """All modified Python files compile without syntax errors (pass_to_pass)."""
    files_to_check = [
        f'{REPO}/openhands/integrations/service_types.py',
        f'{REPO}/openhands/app_server/user/user_router.py',
        f'{REPO}/openhands/app_server/user/user_context.py',
        f'{REPO}/openhands/app_server/user/auth_user_context.py',
        f'{REPO}/openhands/app_server/user/specifiy_user_context.py',
        f'{REPO}/openhands/server/user_auth/user_auth.py',
        f'{REPO}/openhands/server/routes/git.py',
    ]
    r = subprocess.run(
        [sys.executable, '-m', 'py_compile'] + files_to_check,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_new_unit_tests_exist():
    """New unit test file for git info endpoint exists (pass_to_pass)."""
    test_file = REPO / 'tests' / 'unit' / 'app_server' / 'test_user_git_info.py'
    assert test_file.exists(), "New unit test file test_user_git_info.py should exist"
    content = test_file.read_text()
    assert 'TestGetCurrentUserGitInfo' in content, "Test class should exist in new test file"


def test_unit_tests_pass():
    """New unit tests for git info pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/unit/app_server/test_user_git_info.py', '-v'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout}\n{r.stderr}"
