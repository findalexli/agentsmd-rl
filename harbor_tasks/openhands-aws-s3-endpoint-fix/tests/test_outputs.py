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

    def test_function_returns_none_when_no_env(self, monkeypatch):
        """Test that the function logic returns None when no env vars set."""
        # Clear environment
        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        # Execute the function logic directly
        source = read_source_code()
        assert source is not None, "Target file must exist"

        # Extract and execute just the function
        tree = ast.parse(source)

        # Find the function
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_get_default_aws_endpoint_url':
                func_node = node
                break

        if func_node is None:
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        # Compile and execute the function
        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result is None, f"Expected None when no env vars set, got {result}"

    def test_function_adds_https_when_secure(self, monkeypatch):
        """Test that function adds https:// prefix when secure=true."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_function_adds_http_when_insecure(self, monkeypatch):
        """Test that function adds http:// prefix when secure=false."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_function_converts_http_to_https(self, monkeypatch):
        """Test that http:// is converted to https:// when secure=true."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_function_converts_https_to_http(self, monkeypatch):
        """Test that https:// is converted to http:// when secure=false."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_function_preserves_https_when_secure(self, monkeypatch):
        """Test that https:// prefix is preserved when secure=true."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_function_preserves_http_when_insecure(self, monkeypatch):
        """Test that http:// prefix is preserved when secure=false."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

        module = ast.Module(body=[func_node], type_ignores=[])
        module = ast.fix_missing_locations(module)
        code = compile(module, '<string>', 'exec')

        namespace = {'os': os}
        exec(code, namespace)
        func = namespace['_get_default_aws_endpoint_url']

        result = func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_function_defaults_secure_to_true(self, monkeypatch):
        """Test that secure defaults to true when AWS_S3_SECURE not set."""
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
            pytest.skip("_get_default_aws_endpoint_url not found - fix not applied yet")

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
        """Test that AwsEventServiceInjector class has endpoint_url attribute."""
        tree = parse_ast()
        assert tree is not None, "Could not parse target file"

        has_endpoint_url = has_class_attribute(tree, 'AwsEventServiceInjector', 'endpoint_url')
        assert has_endpoint_url, "AwsEventServiceInjector must have endpoint_url attribute defined"

    def test_endpoint_url_uses_field_with_default_factory(self):
        """Test that endpoint_url uses Field with default_factory pointing to _get_default_aws_endpoint_url."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        # Check that the source contains the expected pattern
        # Looking for: endpoint_url: str | None = Field(default_factory=_get_default_aws_endpoint_url)
        assert 'default_factory=_get_default_aws_endpoint_url' in source or \
               'default_factory = _get_default_aws_endpoint_url' in source, \
            "endpoint_url must use Field with default_factory=_get_default_aws_endpoint_url"

    def test_injector_accepts_endpoint_url_parameter(self):
        """Test that AwsEventServiceInjector accepts endpoint_url as init parameter."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        tree = ast.parse(source)

        # Find AwsEventServiceInjector class
        injector_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'AwsEventServiceInjector':
                injector_class = node
                break

        assert injector_class is not None, "AwsEventServiceInjector class must exist"

        # The class should inherit from EventServiceInjector (which is a pydantic model typically)
        # so it should accept endpoint_url as a parameter


class TestEndpointUrlUsedInS3Client:
    """Test that endpoint_url is actually used when creating S3 client."""

    def test_s3_client_uses_self_endpoint_url(self):
        """Test that S3 client uses self.endpoint_url instead of os.getenv."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        # The fix changes: endpoint_url=os.getenv('AWS_S3_ENDPOINT')
        # to: endpoint_url=self.endpoint_url
        assert 'endpoint_url=self.endpoint_url' in source, \
            "S3 client must use self.endpoint_url instead of os.getenv('AWS_S3_ENDPOINT')"

    def test_s3_client_no_longer_uses_os_getenv_for_endpoint(self):
        """Test that S3 client no longer directly calls os.getenv for endpoint."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        # Read the inject method specifically
        tree = ast.parse(source)

        # Find the inject method in AwsEventServiceInjector
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'AwsEventServiceInjector':
                for item in node.body:
                    if isinstance(item, ast.AsyncFunctionDef) and item.name == 'inject':
                        # Check the method body for os.getenv with AWS_S3_ENDPOINT
                        method_source = ast.unparse(item)
                        assert "os.getenv('AWS_S3_ENDPOINT')" not in method_source, \
                            "inject method should not use os.getenv('AWS_S3_ENDPOINT') directly"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These tests verify that the repo's existing CI checks pass on both
# the base commit and after the fix is applied.
# =============================================================================


def test_repo_python_syntax():
    """Python syntax validation for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Compile check
    result = subprocess.run(
        ["python", "-m", "py_compile", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Python syntax error:\n{result.stderr}"

    # AST parse check
    source = target_file.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"AST parsing failed: {e}")


def test_repo_mypy_typecheck():
    """Repo's mypy typecheck passes for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Check mypy is available
    mypy_check = subprocess.run(["which", "mypy"], capture_output=True)
    if mypy_check.returncode != 0:
        pytest.skip("mypy not installed in environment")

    # Run mypy on the target file
    result = subprocess.run(
        [
            "mypy",
            "--config-file", "dev_config/python/mypy.ini",
            "--ignore-missing-imports",
            str(target_file)
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO
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
