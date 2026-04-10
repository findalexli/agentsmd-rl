"""Tests for GitLab resolver org routing PR #13755.

Tests verify:
1. resolve_org_for_repo is imported and called with correct arguments
2. SaasConversationStore.get_resolver_instance is used instead of initialize_conversation
3. resolver_org_id is passed to ResolverUserContext in V1 path
4. send_summary_instruction renamed to should_request_summary in callback processors
"""

import ast
import sys
from pathlib import Path

import pytest

REPO_DIR = Path('/workspace/openhands')
GITLAB_VIEW_PATH = REPO_DIR / 'enterprise' / 'integrations' / 'gitlab' / 'gitlab_view.py'
GITHUB_VIEW_PATH = REPO_DIR / 'enterprise' / 'integrations' / 'github' / 'github_view.py'


class GitLabViewASTInspector:
    """AST inspector for gitlab_view.py changes."""

    def __init__(self, source_code: str):
        self.tree = ast.parse(source_code)
        self.source_lines = source_code.split('\n')

    def has_import(self, module: str, name: str) -> bool:
        """Check if a specific import exists."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == module:
                    for alias in node.names:
                        if alias.name == name:
                            return True
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == f'{module}.{name}':
                        return True
        return False

    def has_function_call(self, func_name: str, in_method: str = None) -> list:
        """Find all calls to a specific function."""
        calls = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node.func)
                if call_name and func_name in call_name:
                    # Check if inside specific method
                    if in_method:
                        parent = self._get_parent_function(node)
                        if parent and parent.name == in_method:
                            calls.append(node)
                    else:
                        calls.append(node)
        return calls

    def _get_call_name(self, func) -> str:
        """Get the full name of a function call."""
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return f'{self._get_call_name(func.value)}.{func.attr}' if hasattr(func.value, 'attr') else f'{func.value}.{func.attr}'
        return None

    def _get_parent_function(self, node) -> ast.FunctionDef:
        """Get the parent function definition of a node."""
        for parent in ast.walk(self.tree):
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for child in ast.walk(parent):
                    if child is node and child != parent:
                        return parent
        return None

    def get_method_source(self, method_name: str) -> str:
        """Get source code of a specific method."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
                start_line = node.lineno - 1
                end_line = node.end_lineno
                return '\n'.join(self.source_lines[start_line:end_line])
        return ''

    def has_attribute_in_constructor_call(self, class_name: str, attr_name: str) -> bool:
        """Check if a class constructor call includes a specific attribute."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node.func)
                if call_name and class_name in call_name:
                    for keyword in node.keywords:
                        if keyword.arg == attr_name:
                            return True
        return False


@pytest.fixture
def gitlab_ast():
    """Load gitlab_view.py AST."""
    if not GITLAB_VIEW_PATH.exists():
        pytest.skip("gitlab_view.py not found")
    source = GITLAB_VIEW_PATH.read_text()
    return GitLabViewASTInspector(source)


@pytest.fixture
def github_ast():
    """Load github_view.py AST."""
    if not GITHUB_VIEW_PATH.exists():
        pytest.skip("github_view.py not found")
    source = GITHUB_VIEW_PATH.read_text()
    return GitLabViewASTInspector(source)


# Fail-to-pass tests: These should fail on base commit, pass on fix


def test_resolve_org_for_repo_imported(gitlab_ast):
    """V0: resolve_org_for_repo is imported from resolver_org_router."""
    assert gitlab_ast.has_import(
        'integrations.resolver_org_router', 'resolve_org_for_repo'
    ), "resolve_org_for_repo should be imported from integrations.resolver_org_router"


def test_resolve_org_for_repo_called_in_initialize(gitlab_ast):
    """V0: resolve_org_for_repo is called in initialize_new_conversation."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    assert 'resolve_org_for_repo' in method_source, \
        "initialize_new_conversation should call resolve_org_for_repo"


def test_resolve_org_for_repo_called_with_correct_args(gitlab_ast):
    """V0: resolve_org_for_repo is called with provider='gitlab'."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    # Check for the call pattern
    assert "provider='gitlab'" in method_source, \
        "resolve_org_for_repo should be called with provider='gitlab'"
    assert "full_repo_name=self.full_repo_name" in method_source, \
        "resolve_org_for_repo should be called with full_repo_name"
    assert "keycloak_user_id=self.user_info.keycloak_user_id" in method_source, \
        "resolve_org_for_repo should be called with keycloak_user_id"


def test_saas_conversation_store_imported(gitlab_ast):
    """V0: SaasConversationStore is imported."""
    assert gitlab_ast.has_import(
        'storage.saas_conversation_store', 'SaasConversationStore'
    ), "SaasConversationStore should be imported from storage.saas_conversation_store"


def test_initialize_conversation_not_imported(gitlab_ast):
    """V0: initialize_conversation is NOT imported (removed)."""
    assert not gitlab_ast.has_import('openhands.server.services.conversation_service', 'initialize_conversation'),         "initialize_conversation should not be imported (use SaasConversationStore instead)"


def test_get_resolver_instance_called(gitlab_ast):
    """V0: SaasConversationStore.get_resolver_instance is called."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    assert 'SaasConversationStore.get_resolver_instance' in method_source or \
           'get_resolver_instance' in method_source, \
        "initialize_new_conversation should call SaasConversationStore.get_resolver_instance"


def test_get_resolver_instance_passes_resolver_org_id(gitlab_ast):
    """V0: get_resolver_instance receives resolved_org_id."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    # Check that resolved_org_id is passed to get_resolver_instance
    assert 'self.resolved_org_id' in method_source, \
        "get_resolver_instance should receive self.resolved_org_id"


def test_resolver_org_id_stored_on_self(gitlab_ast):
    """V0: resolved_org_id is stored on the instance."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    assert 'self.resolved_org_id' in method_source, \
        "resolved_org_id should be stored on self (self.resolved_org_id = ...)"


# V1 path tests


def test_resolver_user_context_receives_org_id(gitlab_ast):
    """V1: ResolverUserContext receives resolver_org_id parameter."""
    method_source = gitlab_ast.get_method_source('_create_v1_conversation')
    assert 'resolver_org_id=self.resolved_org_id' in method_source, \
        "ResolverUserContext constructor should receive resolver_org_id"


# GitHub callback processor tests


def test_github_callback_uses_should_request_summary(github_ast):
    """GitHub callback processor uses should_request_summary parameter."""
    method_source = github_ast.get_method_source('_create_github_v1_callback_processor')
    assert 'should_request_summary=self.send_summary_instruction' in method_source, \
        "GitHub _create_github_v1_callback_processor should use should_request_summary parameter"


# Pass-to-pass tests (verify structure is correct)


def test_get_default_conversation_title_imported(gitlab_ast):
    """get_default_conversation_title is imported for creating metadata."""
    assert gitlab_ast.has_import(
        'openhands.utils.conversation_summary', 'get_default_conversation_title'
    ), "get_default_conversation_title should be imported"


def test_manual_conversation_metadata_creation(gitlab_ast):
    """ConversationMetadata is created manually instead of via initialize_conversation."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    assert 'ConversationMetadata(' in method_source, \
        "ConversationMetadata should be instantiated directly in initialize_new_conversation"


def test_conversation_id_generated_via_uuid(gitlab_ast):
    """conversation_id is generated via uuid4().hex."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    assert 'uuid4().hex' in method_source, \
        "conversation_id should be generated via uuid4().hex"


def test_save_metadata_called(gitlab_ast):
    """store.save_metadata is called with the conversation metadata."""
    method_source = gitlab_ast.get_method_source('initialize_new_conversation')
    assert 'store.save_metadata(conversation_metadata)' in method_source or \
           'await store.save_metadata' in method_source, \
        "store.save_metadata should be called with conversation_metadata"


# Pass-to-pass tests: CI/CD validation (repo's own checks)

def test_repo_pre_commit_lint():
    """Repo's pre-commit hooks pass on modified files (pass_to_pass)."""
    import subprocess
    import os
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~')}/.local/bin:{env.get('PATH', '')}"
    subprocess.run(['pip', 'install', 'pre-commit==4.2.0', '-q'], check=True, env=env)
    r = subprocess.run(
        ['pre-commit', 'run', '--files',
         'enterprise/integrations/gitlab/gitlab_view.py',
         'enterprise/integrations/github/github_view.py',
         '--config', 'enterprise/dev_config/python/.pre-commit-config.yaml'],
        capture_output=True, text=True, cwd=REPO_DIR, timeout=300, env=env
    )
    assert r.returncode == 0, f"Pre-commit failed:\n{r.stdout}\n{r.stderr}"

def test_repo_enterprise_integration_tests():
    """Enterprise integration unit tests pass (pass_to_pass)."""
    import subprocess
    import os
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~')}/.local/bin:{env.get('PATH', '')}"
    subprocess.run(['pip', 'install', 'poetry', '-q'], check=True, env=env)
    install = subprocess.run(
        ['poetry', '-C', 'enterprise', 'install', '--with', 'dev,test', '-q'],
        capture_output=True, text=True, cwd=REPO_DIR, timeout=400, env=env
    )
    assert install.returncode == 0, f"Poetry install failed:\n{install.stderr[-500:]}"
    test_files = [
        'tests/unit/integrations/gitlab/test_gitlab_service.py',
        'tests/unit/integrations/gitlab/test_gitlab_manager.py',
        'tests/unit/integrations/github/test_github_manager.py',
        'tests/unit/integrations/test_resolver_context.py',
        'tests/unit/integrations/test_resolver_org_router.py'
    ]
    test_env = env.copy()
    test_env['PYTHONPATH'] = f'{REPO_DIR}:{REPO_DIR}/enterprise'
    r = subprocess.run(
        ['poetry', '-C', 'enterprise', 'run', 'pytest', '-v'] + test_files,
        capture_output=True, text=True, cwd=REPO_DIR, timeout=300, env=test_env
    )
    assert r.returncode == 0, f"Enterprise integration tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

# AST-based static structure checks (should be origin: static)

def test_gitlab_view_syntax_valid():
    """GitLab view file has valid Python syntax (pass_to_pass)."""
    import ast
    if not GITLAB_VIEW_PATH.exists():
        import pytest
        pytest.skip("gitlab_view.py not found")
    source = GITLAB_VIEW_PATH.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        import pytest
        pytest.fail(f"gitlab_view.py has syntax error: {e}")

def test_github_view_syntax_valid():
    """GitHub view file has valid Python syntax (pass_to_pass)."""
    import ast
    if not GITHUB_VIEW_PATH.exists():
        import pytest
        pytest.skip("github_view.py not found")
    source = GITHUB_VIEW_PATH.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        import pytest
        pytest.fail(f"github_view.py has syntax error: {e}")

def test_enterprise_tests_exist():
    """Enterprise tests directory exists with GitLab/GitHub tests (pass_to_pass)."""
    enterprise_tests = REPO_DIR / 'enterprise' / 'tests' / 'unit' / 'integrations'
    gitlab_tests = enterprise_tests / 'gitlab'
    github_tests = enterprise_tests / 'github'
    assert gitlab_tests.exists(), "GitLab tests directory should exist"
    assert github_tests.exists(), "GitHub tests directory should exist"
    gitlab_test_files = list(gitlab_tests.glob('test_*.py'))
    github_test_files = list(github_tests.glob('test_*.py'))
    assert len(gitlab_test_files) > 0, "GitLab tests should exist"
    assert len(github_test_files) > 0, "GitHub tests should exist"

def test_gitlab_view_imports_resolve():
    """GitLab view imports are syntactically valid (pass_to_pass)."""
    import ast
    if not GITLAB_VIEW_PATH.exists():
        import pytest
        pytest.skip("gitlab_view.py not found")
    source = GITLAB_VIEW_PATH.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module is not None or node.level > 0, f"Invalid import at line {node.lineno}"

def test_github_view_imports_resolve():
    """GitHub view imports are syntactically valid (pass_to_pass)."""
    import ast
    if not GITHUB_VIEW_PATH.exists():
        import pytest
        pytest.skip("github_view.py not found")
    source = GITHUB_VIEW_PATH.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module is not None or node.level > 0, f"Invalid import at line {node.lineno}"

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
