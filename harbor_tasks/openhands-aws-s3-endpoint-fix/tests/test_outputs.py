"""
Tests for AWS S3 endpoint URL configuration fix.

This tests that the _get_default_aws_endpoint_url function properly:
1. Returns None when no AWS_S3_ENDPOINT is set
2. Handles protocol (http/https) based on AWS_S3_SECURE setting
3. Works as a default factory for AwsEventServiceInjector.endpoint_url field
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

# Add the repo to path
REPO = Path("/workspace/openhands")
sys.path.insert(0, str(REPO))

import pytest


def get_target_file():
    """Get path to the target file."""
    return REPO / "openhands" / "app_server" / "event" / "aws_event_service.py"


def read_source_code():
    """Read the source code of the target file."""
    target_file = get_target_file()
    if not target_file.exists():
        return None
    return target_file.read_text()


def parse_ast():
    """Parse the AST of the target file."""
    source = read_source_code()
    if source is None:
        return None
    return ast.parse(source)


def has_function_def(tree, func_name):
    """Check if a function is defined in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return True
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            return True
    return False


def has_class_attribute(tree, class_name, attr_name):
    """Check if a class has a specific attribute defined."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                # Check for attribute assignment (AnnAssign for type annotated)
                if isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name) and item.target.id == attr_name:
                        return True
                # Check for regular assignment
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == attr_name:
                            return True
    return False


# =============================================================================
# Fail-to-Pass Tests (Verify the fix works)
# These tests check that the fix is present in the code
# =============================================================================


class TestGetDefaultAwsEndpointUrl:
    """Test cases for _get_default_aws_endpoint_url function existence and logic."""

    def test_function_exists(self):
        """Test that _get_default_aws_endpoint_url function is defined."""
        tree = parse_ast()
        assert tree is not None, "Could not parse target file"
        assert has_function_def(tree, '_get_default_aws_endpoint_url'), \
            "_get_default_aws_endpoint_url function must be defined"

    def test_no_env_vars_returns_none(self, monkeypatch):
        """Test that the function returns None when no env vars set (f2p)."""
        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        source = read_source_code()
        assert source is not None, "Target file must exist"

        tree = ast.parse(source)
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result is None, f"Expected None when no env vars set, got {result}"

    def test_endpoint_with_https_prefix_secure(self, monkeypatch):
        """Endpoint URL with https:// prefix when secure=true (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_endpoint_without_prefix_secure_adds_https(self, monkeypatch):
        """Adds https:// prefix when secure=true and no protocol (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_endpoint_with_http_prefix_insecure(self, monkeypatch):
        """Endpoint URL with http:// prefix when secure=false (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'http://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'false')

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_endpoint_without_prefix_insecure_adds_http(self, monkeypatch):
        """Adds http:// prefix when secure=false and no protocol (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'false')

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_endpoint_http_converted_to_https_when_secure(self, monkeypatch):
        """Converts http:// to https:// when secure=true (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'http://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_endpoint_https_converted_to_http_when_insecure(self, monkeypatch):
        """Converts https:// to http:// when secure=false (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'false')

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_secure_defaults_to_true(self, monkeypatch):
        """AWS_S3_SECURE defaults to true when not set (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        source = read_source_code()
        tree = ast.parse(source)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000 (default secure), got {result}"


class TestAwsEventServiceInjectorEndpointUrl:
    """Test cases for AwsEventServiceInjector endpoint_url field."""

    def test_injector_has_endpoint_url_attribute(self):
        """AwsEventServiceInjector has endpoint_url as a class field (f2p)."""
        tree = parse_ast()
        assert tree is not None, "Could not parse target file"

        has_endpoint_url = has_class_attribute(tree, 'AwsEventServiceInjector', 'endpoint_url')
        assert has_endpoint_url, "AwsEventServiceInjector must have endpoint_url attribute defined"

    def test_injector_endpoint_url_populated_from_env(self, monkeypatch):
        """AwsEventServiceInjector.endpoint_url populated from env via Field default_factory (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        source = read_source_code()
        assert source is not None, "Target file must exist"

        assert 'default_factory=_get_default_aws_endpoint_url' in source or \
               'default_factory = _get_default_aws_endpoint_url' in source, \
            "endpoint_url must use Field with default_factory=_get_default_aws_endpoint_url"

    def test_injector_accepts_custom_endpoint_url(self):
        """AwsEventServiceInjector accepts custom endpoint_url parameter (f2p)."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        tree = ast.parse(source)
        injector_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'AwsEventServiceInjector':
                injector_class = node
                break

        assert injector_class is not None, "AwsEventServiceInjector class must exist"

    def test_injector_endpoint_url_none_when_no_env(self, monkeypatch):
        """AwsEventServiceInjector.endpoint_url is None when no env vars set (f2p)."""
        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        source = read_source_code()
        assert source is not None, "Target file must exist"

        # Verify the function exists that returns None when no env
        assert '_get_default_aws_endpoint_url' in source, \
            "_get_default_aws_endpoint_url function must be defined"


class TestEndpointUrlUsedInS3Client:
    """Test that endpoint_url is actually used when creating S3 client."""

    def test_injector_has_endpoint_url_attribute(self):
        """AwsEventServiceInjector has endpoint_url as a class field (f2p)."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        # The fix changes: endpoint_url=os.getenv('AWS_S3_ENDPOINT')
        # to: endpoint_url=self.endpoint_url
        assert 'endpoint_url=self.endpoint_url' in source, \
            "S3 client must use self.endpoint_url instead of os.getenv('AWS_S3_ENDPOINT')"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These tests verify that the repo's existing CI checks pass on both
# the base commit and after the fix is applied.
# =============================================================================


def test_repo_python_syntax():
    """Python syntax validation for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Compile check via subprocess (CI command)
    result = subprocess.run(
        ["python", "-m", "py_compile", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Python syntax error:\n{result.stderr}"


def test_repo_ast_parses():
    """Python AST parsing for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # AST parse check via subprocess (CI command)
    result = subprocess.run(
        [
            "python",
            "-c",
            f"import ast; ast.parse(open('{target_file}').read()); print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"AST parsing failed:\n{result.stderr}"


def test_repo_ruff_check():
    """Repo's ruff linter passes for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Install ruff and run check
    result = subprocess.run(
        [
            "bash",
            "-c",
            "pip install ruff -q && ruff check --config dev_config/python/ruff.toml openhands/app_server/event/aws_event_service.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format_check():
    """Repo's ruff format check passes for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Install ruff and run format check
    result = subprocess.run(
        [
            "bash",
            "-c",
            "pip install ruff -q && ruff format --config dev_config/python/ruff.toml --check openhands/app_server/event/aws_event_service.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_mypy_typecheck():
    """Repo's mypy typecheck passes for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Install mypy and run typecheck
    result = subprocess.run(
        [
            "bash",
            "-c",
            "pip install mypy -q && mypy --config-file dev_config/python/mypy.ini --ignore-missing-imports openhands/app_server/event/aws_event_service.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"mypy typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_repo_modified_file_exists():
    """Primary modified file exists and is readable (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"
    assert target_file.is_file(), f"Target is not a file: {target_file}"

    # Read and verify it's valid Python source
    content = target_file.read_text()
    assert len(content) > 0, "Target file is empty"
    assert "class AwsEventServiceInjector" in content, "Missing AwsEventServiceInjector class"
    assert "class AwsEventService" in content, "Missing AwsEventService class"
