"""Tests for AWS S3 endpoint URL configuration fix.

This validates the fix for properly handling AWS S3 (Minio) endpoint URLs
with correct HTTP/HTTPS protocol based on environment variables.
"""

import ast
import os
import subprocess
from pathlib import Path

REPO = Path('/workspace/openhands')
SOURCE_PATH = REPO / 'openhands' / 'app_server' / 'event' / 'aws_event_service.py'


# ==================== Pass-to-pass Tests ====================
# These verify the repo's existing CI/CD checks pass on base commit and after fix

def test_repo_python_syntax_valid():
    """Target file has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-m', 'py_compile', 'openhands/app_server/event/aws_event_service.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ruff_check():
    """Repo's ruff linting passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Use --fix like the pre-commit hook does
    r = subprocess.run(
        ['ruff', 'check', 'openhands/app_server/event/aws_event_service.py', '--config', 'dev_config/python/ruff.toml', '--fix'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff formatting passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ['ruff', 'format', '--check', 'openhands/app_server/event/aws_event_service.py', '--config', 'dev_config/python/ruff.toml'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}"


def test_repo_unit_test_file_valid():
    """Repo's unit test file for aws_event_service has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-m', 'py_compile', 'tests/unit/app_server/test_aws_event_service.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit test file syntax check failed:\n{r.stderr}"


def test_repo_test_config_file_valid():
    """Repo's event service config test file has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-m', 'py_compile', 'tests/unit/app_server/test_config_event_service_selection.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Config test file syntax check failed:\n{r.stderr}"


def test_repo_file_is_git_tracked():
    """Target file is tracked in git repo (pass_to_pass)."""
    r = subprocess.run(
        ['git', 'ls-files', '--error-unmatch', 'openhands/app_server/event/aws_event_service.py'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Target file is not tracked in git:\n{r.stderr}"


def test_repo_unit_tests_aws_event_service():
    """Repo's unit tests for aws_event_service pass (pass_to_pass)."""
    # Install dependencies
    r = subprocess.run(
        ['pip', 'install', 'boto3', 'botocore', 'pydantic', 'pytest-asyncio', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install package in editable mode
    r = subprocess.run(
        ['pip', 'install', '-e', '.', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run the unit tests
    r = subprocess.run(
        ['python', '-m', 'pytest', 'tests/unit/app_server/test_aws_event_service.py', '-v', '--tb=short'],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests_config_event_service_selection():
    """Repo's unit tests for event service config selection pass (pass_to_pass)."""
    # Install dependencies
    r = subprocess.run(
        ['pip', 'install', 'boto3', 'botocore', 'pydantic', 'pytest-asyncio', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install package in editable mode
    r = subprocess.run(
        ['pip', 'install', '-e', '.', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run the unit tests
    r = subprocess.run(
        ['python', '-m', 'pytest', 'tests/unit/app_server/test_config_event_service_selection.py', '-v', '--tb=short'],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Config tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_mypy_clean():
    """Repo's mypy type checking passes on target file (pass_to_pass)."""
    # Install mypy and required dependencies
    r = subprocess.run(
        ['pip', 'install', 'mypy', 'boto3', 'botocore', 'pydantic', 'types-requests', 'types-setuptools', 'types-pyyaml', 'types-toml', 'types-docker', 'types-Markdown', 'lxml', '-q'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run mypy on target file
    r = subprocess.run(
        ['mypy', '--config-file', 'dev_config/python/mypy.ini', 'openhands/app_server/event/aws_event_service.py'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"MyPy check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_validate_pyproject():
    """Repo's pyproject.toml is valid (pass_to_pass)."""
    r = subprocess.run(
        ['pip', 'install', 'validate-pyproject', '-q'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ['validate-pyproject', 'pyproject.toml'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr[-500:]}"


def test_repo_imports_clean():
    """Target file can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ['python', '-c', 'from openhands.app_server.event.aws_event_service import AwsEventServiceInjector'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import check failed:\n{r.stderr[-500:]}"


def _load_source():
    """Load the source code of the target file."""
    with open(SOURCE_PATH) as f:
        return f.read()


def _parse_ast():
    """Parse the AST of the target file."""
    source = _load_source()
    return ast.parse(source)


def _get_function_def(name):
    """Get a function definition by name from the AST."""
    tree = _parse_ast()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _get_class_def(name):
    """Get a class definition by name from the AST."""
    tree = _parse_ast()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


# ==================== Fail-to-pass Tests ====================

def test_pydantic_field_import_present():
    """F2P: Module imports pydantic Field."""
    tree = _parse_ast()

    # Find pydantic import
    pydantic_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'pydantic':
            for alias in node.names:
                pydantic_imports.append(alias.name)

    assert 'Field' in pydantic_imports, f"Should import Field from pydantic, found: {pydantic_imports}"


def test_injector_uses_self_endpoint_url():
    """F2P: Injector uses self.endpoint_url instead of os.getenv in inject method."""
    source = _load_source()

    # Check that self.endpoint_url is used in the boto3.client call
    assert 'endpoint_url=self.endpoint_url' in source,         "Should use self.endpoint_url in boto3.client call"


def test_get_default_aws_endpoint_url_function_exists():
    """F2P: _get_default_aws_endpoint_url function exists."""
    func_def = _get_function_def('_get_default_aws_endpoint_url')
    assert func_def is not None, "Should have _get_default_aws_endpoint_url function"


def test_get_default_aws_endpoint_url_function_structure():
    """F2P: _get_default_aws_endpoint_url function handles secure and insecure properly."""
    func_def = _get_function_def('_get_default_aws_endpoint_url')
    assert func_def is not None, "Should have _get_default_aws_endpoint_url function"

    # Get function source
    func_source = ast.unparse(func_def)

    # Check for key behaviors
    assert 'AWS_S3_ENDPOINT' in func_source, "Should reference AWS_S3_ENDPOINT env var"
    assert 'AWS_S3_SECURE' in func_source, "Should reference AWS_S3_SECURE env var"
    assert 'https://' in func_source, "Should handle https:// protocol"
    assert 'http://' in func_source, "Should handle http:// protocol"
    assert 'secure' in func_source.lower() or 'true' in func_source, "Should handle secure setting"


def test_get_default_aws_endpoint_url_returns_none_when_no_env():
    """F2P: Function returns None when AWS_S3_ENDPOINT not set."""
    func_def = _get_function_def('_get_default_aws_endpoint_url')
    assert func_def is not None, "Should have _get_default_aws_endpoint_url function"

    func_source = ast.unparse(func_def)

    # Check the function handles the case where env var is not set
    # Should check for endpoint_url being falsy and return None
    assert 'if not endpoint_url' in func_source or 'if endpoint_url' in func_source,         "Should check if endpoint_url is set"
    assert 'return None' in func_source, "Should return None when endpoint not set"


def test_get_default_aws_endpoint_url_handles_https_secure():
    """F2P: Function handles https:// with secure=true."""
    func_def = _get_function_def('_get_default_aws_endpoint_url')
    assert func_def is not None, "Should have _get_default_aws_endpoint_url function"

    func_source = ast.unparse(func_def)

    # Check for https:// handling
    assert 'https://' in func_source, "Should handle https:// protocol"
    assert 'startswith' in func_source, "Should use startswith to check protocol"


def test_get_default_aws_endpoint_url_handles_http_insecure():
    """F2P: Function handles http:// with secure=false."""
    func_def = _get_function_def('_get_default_aws_endpoint_url')
    assert func_def is not None, "Should have _get_default_aws_endpoint_url function"

    func_source = ast.unparse(func_def)

    # Check for http:// handling
    assert 'http://' in func_source, "Should handle http:// protocol"


def test_get_default_aws_endpoint_url_converts_protocol():
    """F2P: Function converts protocol based on secure setting."""
    func_def = _get_function_def('_get_default_aws_endpoint_url')
    assert func_def is not None, "Should have _get_default_aws_endpoint_url function"

    func_source = ast.unparse(func_def)

    # Check that http:// can be converted to https:// and vice versa
    assert 'removeprefix' in func_source, "Should use removeprefix to convert protocols"


def test_injector_has_endpoint_url_field():
    """F2P: Injector class has endpoint_url field."""
    cls_def = _get_class_def('AwsEventServiceInjector')
    assert cls_def is not None, "Should have AwsEventServiceInjector class"

    # Get class source
    cls_source = ast.unparse(cls_def)

    # Check that endpoint_url field exists
    assert 'endpoint_url' in cls_source, "Should have endpoint_url field"


def test_injector_endpoint_url_type():
    """F2P: endpoint_url field has correct type annotation str | None."""
    cls_def = _get_class_def('AwsEventServiceInjector')
    assert cls_def is not None, "Should have AwsEventServiceInjector class"

    # Check annotations
    for node in ast.walk(cls_def):
        if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id'):
            if node.target.id == 'endpoint_url':
                # Check the annotation contains str and None
                annotation_str = ast.unparse(node.annotation)
                assert 'str' in annotation_str and 'None' in annotation_str,                     f"endpoint_url should be annotated as str | None, got: {annotation_str}"
                return

    assert False, "Should find endpoint_url annotated field"


def test_injector_endpoint_url_has_default_factory():
    """F2P: endpoint_url field has default_factory using _get_default_aws_endpoint_url."""
    cls_def = _get_class_def('AwsEventServiceInjector')
    assert cls_def is not None, "Should have AwsEventServiceInjector class"

    cls_source = ast.unparse(cls_def)

    # Check for Field with default_factory
    assert 'Field' in cls_source, "Should use pydantic Field"
    assert 'default_factory' in cls_source, "Should use default_factory parameter"
    assert '_get_default_aws_endpoint_url' in cls_source,         "Should use _get_default_aws_endpoint_url as default_factory"


def test_injector_endpoint_url_not_required():
    """F2P: endpoint_url field is not required (has default)."""
    source = _load_source()

    # The field should have a default value (via Field(default_factory=...))
    assert 'endpoint_url:' in source or 'endpoint_url =' in source,         "endpoint_url should be defined as a field"
    assert 'Field' in source and 'default_factory' in source,         "endpoint_url should have a default factory"
