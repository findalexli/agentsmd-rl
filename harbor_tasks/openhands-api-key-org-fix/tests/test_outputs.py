"""Tests for API key organization association fix.

These tests verify that the save_app_conversation_info() method correctly uses
the API key's org_id when available, falling back to user.current_org_id for
legacy API keys and cookie-based authentication.
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID, uuid4

# Add enterprise code to path
sys.path.insert(0, str(Path('/workspace/OpenHands')))

import pytest


# Repo path for pass-to-pass tests
REPO = Path('/workspace/OpenHands')


# Mock classes to simulate the database and context objects
@dataclass
class MockUser:
    """Mock User model."""
    id: UUID
    current_org_id: UUID | None = None


@dataclass
class MockStoredConversationMetadata:
    """Mock StoredConversationMetadata model."""
    conversation_id: str
    conversation_version: str = 'V1'
    title: str = ''
    sandbox_id: str = ''
    created_at: str = ''
    last_updated_at: str = ''
    parent_conversation_id: str | None = None


@dataclass
class MockStoredConversationMetadataSaas:
    """Mock StoredConversationMetadataSaas model."""
    conversation_id: str
    user_id: UUID
    org_id: UUID | None = None


@dataclass
class MockAppConversationInfo:
    """Mock AppConversationInfo model."""
    id: UUID
    created_by_user_id: str
    sandbox_id: str
    title: str


class MockScalarResult:
    """Mock SQLAlchemy scalar result."""
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value

    def scalar_one_or_none(self):
        return self._value


class MockResult:
    """Mock SQLAlchemy result."""
    def __init__(self, value=None, rows=None):
        self._value = value
        self._rows = rows or []

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return MockScalarResult(self._value)

    def first(self):
        if self._rows:
            return self._rows[0]
        return self._value

    def all(self):
        return self._rows


class MockAsyncSession:
    """Mock SQLAlchemy async session."""
    def __init__(self):
        self.committed = False
        self.added = []

    async def execute(self, query):
        # This will be overridden in tests
        return MockResult()

    async def commit(self):
        self.committed = True

    def add(self, obj):
        self.added.append(obj)

    def expire_all(self):
        pass


# Mock UserAuth classes
class MockUserAuthWithOrg:
    """Mock UserAuth that has API key with org_id."""
    def __init__(self, user_id: str, api_key_org_id: UUID | None):
        self._user_id = user_id
        self._api_key_org_id = api_key_org_id

    async def get_user_id(self) -> str:
        return self._user_id

    def get_api_key_org_id(self) -> UUID | None:
        return self._api_key_org_id


class MockUserAuthLegacy:
    """Mock UserAuth for legacy API key without org_id."""
    def __init__(self, user_id: str):
        self._user_id = user_id

    async def get_user_id(self) -> str:
        return self._user_id

    def get_api_key_org_id(self) -> None:
        return None


class MockUserAuthNoMethod:
    """Mock UserAuth without get_api_key_org_id method (cookie auth)."""
    def __init__(self, user_id: str):
        self._user_id = user_id

    async def get_user_id(self) -> str:
        return self._user_id


class MockUserContext:
    """Base user context."""
    def __init__(self, user_id: str):
        self._user_id = user_id

    async def get_user_id(self) -> str | None:
        return self._user_id


class MockUserContextWithAuth(MockUserContext):
    """User context with user_auth attribute (API key auth)."""
    def __init__(self, user_auth):
        self.user_auth = user_auth

    async def get_user_id(self) -> str | None:
        return await self.user_auth.get_user_id()


def load_source_file():
    """Load and return the source file content as text."""
    source_path = Path('/workspace/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py')
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    return source_path.read_text()


def check_api_key_org_logic(source_code: str) -> dict:
    """Check if the source code has the API key org_id fix.

    Returns a dict with findings about the fix implementation.
    """
    findings = {
        'has_org_id_variable': False,
        'has_user_context_check': False,
        'has_user_auth_check': False,
        'has_get_api_key_org_id_check': False,
        'has_fallback_to_user_org': False,
        'uses_org_id_in_metadata': False,
    }

    # Check for org_id variable definition
    if 'org_id = user.current_org_id' in source_code or 'org_id = user.current_org_id  # Default fallback' in source_code:
        findings['has_org_id_variable'] = True

    # Check for hasattr(self.user_context, 'user_auth')
    if "hasattr(self.user_context, 'user_auth')" in source_code:
        findings['has_user_context_check'] = True

    # Check for hasattr(user_auth, 'get_api_key_org_id')
    if "hasattr(user_auth, 'get_api_key_org_id')" in source_code:
        findings['has_user_auth_check'] = True

    # Check for get_api_key_org_id() call
    if 'get_api_key_org_id()' in source_code:
        findings['has_get_api_key_org_id_check'] = True

    # Check for fallback pattern (api_key_org_id is not None check)
    if 'api_key_org_id is not None' in source_code:
        findings['has_fallback_to_user_org'] = True

    # Check that org_id is used in StoredConversationMetadataSaas
    if 'org_id=org_id' in source_code or 'org_id = org_id' in source_code:
        findings['uses_org_id_in_metadata'] = True

    return findings


# ===== Fail-to-Pass Tests (regression tests) =====

def test_code_imports_and_syntax():
    """Verify the modified code has valid Python syntax and can be parsed."""
    source_code = load_source_file()

    # Try to parse the Python code
    import ast
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"Source file has syntax error: {e}")

    # Verify key classes exist
    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert 'SaasSQLAppConversationInfoService' in class_names, "Main class not found"

    # Find save_app_conversation_info method
    save_method_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == 'save_app_conversation_info':
            save_method_found = True
            break

    assert save_method_found, "save_app_conversation_info method not found"


def test_api_key_org_id_used_when_available():
    """Test that API key's org_id is used when saving conversation via API key auth.

    This is the main bug fix test: when a user creates an API key in Organization A,
    then switches to Organization B in browser, and uses the API key to create a
    conversation, the conversation should be saved under Organization A (API key's org),
    not Organization B (user's current org).
    """
    source_code = load_source_file()
    findings = check_api_key_org_logic(source_code)

    # The fix must implement all these components
    assert findings['has_org_id_variable'], (
        "Missing org_id variable definition with fallback to user.current_org_id"
    )
    assert findings['has_user_context_check'], (
        "Missing check for user_context.user_auth attribute"
    )
    assert findings['has_user_auth_check'], (
        "Missing check for user_auth.get_api_key_org_id method"
    )
    assert findings['has_get_api_key_org_id_check'], (
        "Missing call to get_api_key_org_id()"
    )
    assert findings['has_fallback_to_user_org'], (
        "Missing fallback logic for when api_key_org_id is None"
    )
    assert findings['uses_org_id_in_metadata'], (
        "Missing use of org_id in StoredConversationMetadataSaas creation"
    )

    # Verify the correct logic flow exists
    # The fix should check: hasattr(self.user_context, 'user_auth')
    assert 'if hasattr(self.user_context, ' in source_code, (
        "Missing hasattr check for user_auth on user_context"
    )

    # The fix should get the user_auth and check for get_api_key_org_id
    assert 'user_auth = self.user_context.user_auth' in source_code or "user_auth = self.user_context.user_auth" in source_code, (
        "Missing assignment of user_auth from user_context"
    )

    # The fix should use the api_key_org_id when not None
    assert 'if api_key_org_id is not None:' in source_code, (
        "Missing check for api_key_org_id is not None"
    )

    # The fix should assign org_id = api_key_org_id
    assert 'org_id = api_key_org_id' in source_code, (
        "Missing assignment of org_id from api_key_org_id"
    )


def test_legacy_api_key_falls_back_to_user_org():
    """Test that legacy API keys (without org_id) fall back to user's current org.

    Legacy API keys created before the org_id feature was added will have
    api_key_org_id = None. In this case, we should fall back to the user's
    current_org_id.
    """
    source_code = load_source_file()

    # The fix should have the fallback pattern:
    # 1. Default org_id to user.current_org_id
    # 2. Only override if api_key_org_id is not None

    # Check for default fallback
    assert 'org_id = user.current_org_id' in source_code, (
        "Missing default org_id assignment from user.current_org_id"
    )

    # Check that the None check is in place for proper fallback
    lines = source_code.split('\n')
    found_fallback_pattern = False
    for i, line in enumerate(lines):
        if 'api_key_org_id is not None' in line:
            # Check previous lines for the org_id default assignment
            for j in range(max(0, i-10), i):
                if 'org_id = user.current_org_id' in lines[j]:
                    found_fallback_pattern = True
                    break
            break

    assert found_fallback_pattern, (
        "Missing proper fallback pattern: org_id should default to user.current_org_id, "
        "then only be overridden if api_key_org_id is not None"
    )


def test_cookie_auth_uses_user_current_org():
    """Test that cookie auth (no API key) uses user's current org.

    When authenticated via browser cookie (no API key), there's no
    get_api_key_org_id method, so we use user's current_org_id.
    This preserves existing behavior for non-API-key authentication.
    """
    source_code = load_source_file()

    # The fix should use hasattr to safely check for get_api_key_org_id
    # This ensures cookie auth (without the method) doesn't crash
    assert "hasattr(user_auth, 'get_api_key_org_id')" in source_code, (
        "Missing hasattr check for get_api_key_org_id - needed for safe cookie auth handling"
    )

    # The fix should check hasattr(self.user_context, 'user_auth') first
    # to handle cases where user_context doesn't have user_auth attribute
    assert "hasattr(self.user_context, 'user_auth')" in source_code, (
        "Missing hasattr check for user_auth on user_context - needed for cookie auth"
    )

    # Verify the structure: outer check for user_auth, inner check for get_api_key_org_id
    lines = source_code.split('\n')
    found_proper_nesting = False
    user_context_check_line = -1

    for i, line in enumerate(lines):
        if "hasattr(self.user_context, 'user_auth')" in line:
            user_context_check_line = i
            # Look for the get_api_key_org_id check within next few lines
            for j in range(i+1, min(i+15, len(lines))):
                if "hasattr(user_auth, 'get_api_key_org_id')" in lines[j]:
                    found_proper_nesting = True
                    break
            break

    assert found_proper_nesting, (
        "Missing proper nested structure: hasattr for user_context.user_auth "
        "should wrap hasattr for get_api_key_org_id"
    )


def test_no_direct_user_current_org_in_metadata_creation():
    """Verify that user.current_org_id is NOT directly used in metadata creation anymore.

    After the fix, the code should use the computed org_id variable instead of
    directly using user.current_org_id when creating StoredConversationMetadataSaas.
    """
    source_code = load_source_file()

    # Find the StoredConversationMetadataSaas creation section
    if 'StoredConversationMetadataSaas(' in source_code:
        # Split and find the section where StoredConversationMetadataSaas is instantiated
        parts = source_code.split('StoredConversationMetadataSaas(')
        if len(parts) > 1:
            for part in parts[1:]:  # Skip first part (before first occurrence)
                # Find the closing parenthesis for this instantiation
                paren_count = 1
                end_idx = 0
                for j, char in enumerate(part):
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            end_idx = j
                            break

                instantiation = part[:end_idx]

                # Check that it uses org_id=org_id (the variable) not org_id=user.current_org_id
                if 'org_id=user.current_org_id' in instantiation:
                    pytest.fail(
                        "Found direct use of user.current_org_id in StoredConversationMetadataSaas creation. "
                        "Should use org_id variable instead."
                    )

                # The fix should use the org_id variable
                assert 'org_id=org_id' in instantiation, (
                    f"StoredConversationMetadataSaas should use org_id=org_id variable, "
                    f"but found: {instantiation[:200]}"
                )
                break


def test_distinctive_fix_lines_present():
    """Test that distinctive lines from the gold patch are present.

    This ensures the specific implementation from the fix is in place.
    """
    source_code = load_source_file()

    # These are distinctive lines from the gold patch
    distinctive_patterns = [
        "# Determine org_id: prefer API key's org_id if authenticated via API key",
        "# Default fallback",
        "if hasattr(self.user_context, 'user_auth')",
        "user_auth = self.user_context.user_auth",
        "if hasattr(user_auth, 'get_api_key_org_id')",
        "api_key_org_id = user_auth.get_api_key_org_id()",
        "if api_key_org_id is not None:",
        "org_id = api_key_org_id",
        "# Create new SAAS metadata with the determined org_id",
    ]

    missing_patterns = []
    for pattern in distinctive_patterns:
        if pattern not in source_code:
            missing_patterns.append(pattern)

    # Most patterns should be present - allow for some variation in comments
    # but the core logic patterns must be there
    critical_patterns = [
        "if hasattr(self.user_context, 'user_auth')",
        "api_key_org_id = user_auth.get_api_key_org_id()",
        "if api_key_org_id is not None:",
        "org_id = api_key_org_id",
    ]

    for pattern in critical_patterns:
        assert pattern in source_code, (
            f"Critical fix pattern missing: '{pattern}'. "
            f"The fix may not be properly implemented."
        )


# ===== Pass-to-Pass Tests (repo CI/CD checks) =====

def test_repo_syntax_check():
    """Repo's Python syntax is valid (pass_to_pass).

    This test verifies that the modified Python file has valid syntax
    and can be compiled without errors. Mirrors CI lint check.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    r = subprocess.run(
        ['python3', '-m', 'py_compile', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ast_parse():
    """Repo's modified file can be parsed by AST (pass_to_pass).

    This test verifies that the modified Python file can be parsed
    into an abstract syntax tree without errors.
    """
    import ast

    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    source_code = target_file.read_text()

    try:
        ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")


def test_repo_enterprise_syntax():
    """Enterprise module files have valid Python syntax (pass_to_pass).

    This test verifies that key Python files in the enterprise module
    have valid syntax and can be compiled.
    """
    enterprise_files = [
        'enterprise/server/utils/saas_app_conversation_info_injector.py',
        'enterprise/tests/unit/storage/test_saas_sql_app_conversation_info_service.py',
    ]

    for rel_path in enterprise_files:
        target_file = REPO / rel_path
        if target_file.exists():
            r = subprocess.run(
                ['python3', '-m', 'py_compile', str(target_file)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert r.returncode == 0, f"Syntax check failed for {rel_path}:\n{r.stderr}"


def test_repo_class_structure():
    """Repo's modified file has expected class structure (pass_to_pass).

    This test verifies that the expected classes and methods exist
    in the modified file.
    """
    import ast

    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    source_code = target_file.read_text()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")

    # Check for expected classes
    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    expected_classes = ['SaasSQLAppConversationInfoService', 'SaasAppConversationInfoServiceInjector']

    for cls in expected_classes:
        assert cls in class_names, f"Expected class '{cls}' not found in source file"

    # Check for expected method
    method_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == 'save_app_conversation_info'
    ]
    assert 'save_app_conversation_info' in method_names, "Method 'save_app_conversation_info' not found"


def test_repo_ruff_lint():
    """Repo's modified file passes ruff linting - critical errors only (pass_to_pass).

    This test verifies that the modified Python file passes ruff for critical
    linter, matching the CI/CD lint checks.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    ruff_config = REPO / 'dev_config' / 'python' / 'ruff.toml'

    # First ensure ruff is installed
    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ['ruff', 'check', '--no-cache', '--config', str(ruff_config),  '--select', 'F', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff found syntax errors:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_ruff_check_target():
    """Enterprise module target file passes enterprise ruff config (pass_to_pass).

    This test runs ruff check with the enterprise-specific config on the
    modified file, matching the CI lint-enterprise-python workflow.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    ruff_config = REPO / 'enterprise' / 'dev_config' / 'python' / 'ruff.toml'

    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ['ruff', 'check', '--no-cache', '--config', str(ruff_config), '--ignore', 'I', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Enterprise ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_ruff_format():
    """Enterprise target file passes ruff format check (pass_to_pass).

    This test verifies that the modified file is properly formatted according
    to the enterprise ruff config, matching CI format checks.
    """
    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    ruff_config = REPO / 'enterprise' / 'dev_config' / 'python' / 'ruff.toml'

    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ['ruff', 'format', '--no-cache', '--config', str(ruff_config), '--check', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Enterprise ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_enterprise_storage_syntax():
    """Enterprise storage test file has valid syntax (pass_to_pass).

    This test verifies that the related enterprise storage test file
    has valid Python syntax, ensuring consistency with the modified module.
    """
    target_file = REPO / 'enterprise' / 'tests' / 'unit' / 'storage' / 'test_saas_sql_app_conversation_info_service.py'
    r = subprocess.run(
        ['python3', '-m', 'py_compile', str(target_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Enterprise storage test syntax check failed:\n{r.stderr}"


def test_repo_enterprise_pytest_unit():
    """Enterprise unit tests pass for related storage module (pass_to_pass).

    This test runs a quick subset of the enterprise unit tests for the
    storage module, verifying the modified code works correctly.
    Mirrors the CI test-enterprise workflow.
    """
    # Install poetry and dependencies
    install_r = subprocess.run(
        ['pip', 'install', 'poetry', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Install enterprise dependencies
    enterprise_dir = REPO / 'enterprise'
    poetry_install = subprocess.run(
        ['poetry', 'install', '--with', 'dev', '-q'],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=enterprise_dir,
    )

    # Run a quick test to verify the module works
    test_path = 'tests/unit/storage/test_saas_sql_app_conversation_info_service.py::TestSaasSQLAppConversationInfoService::test_service_initialization'
    r = subprocess.run(
        [
            'poetry', 'run', 'pytest',
            test_path,
            '-v', '--tb=short'
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=enterprise_dir,
        env={**os.environ, 'PYTHONPATH': '..:.'}
    )
    assert r.returncode == 0, f"Enterprise pytest failed:\n{r.stdout}\n{r.stderr}"


def test_repo_import_structure():
    """Modified file has valid import structure (pass_to_pass).

    This test verifies that all imports in the modified file are
    syntactically valid without actually importing the modules.
    """
    import ast

    target_file = REPO / 'enterprise' / 'server' / 'utils' / 'saas_app_conversation_info_injector.py'
    source_code = target_file.read_text()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")

    # Collect all imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)

    # Verify we found expected imports (basic sanity check)
    assert len(imports) > 0, "No imports found in the file"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
