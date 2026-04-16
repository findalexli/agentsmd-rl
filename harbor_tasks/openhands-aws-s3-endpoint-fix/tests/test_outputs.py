"""
Tests for AWS S3 endpoint URL configuration fix.

These tests verify the BEHAVIOR of the endpoint URL configuration:
1. AwsEventServiceInjector has an endpoint_url field that reads from env vars
2. The endpoint URL protocol is properly handled based on AWS_S3_SECURE setting
3. The S3 client uses the instance's endpoint_url field

Implementation is AGNOSTIC - tests check behavior, not specific function names.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Add the repo to path
REPO = Path("/workspace/openhands")
sys.path.insert(0, str(REPO))


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


def get_endpoint_url_logic(tree):
    """
    Extract the endpoint URL logic from the AST.
    Returns a callable function that computes endpoint URL based on env vars.
    This is implementation-agnostic - it looks for the logic pattern, not a specific name.
    """
    # Strategy 1: Look for a function that checks AWS_S3_ENDPOINT env var
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            source = ast.dump(node)
            # Look for functions that reference AWS_S3_ENDPOINT and AWS_S3_SECURE
            if 'AWS_S3_ENDPOINT' in source and 'AWS_S3_SECURE' in source:
                # Found a candidate function
                module = ast.Module(body=[node], type_ignores=[])
                module = ast.fix_missing_locations(module)
                code = compile(module, '<string>', 'exec')
                namespace = {'os': os}
                exec(code, namespace)
                # Return the function from the namespace
                for key, value in namespace.items():
                    if callable(value) and key != 'os':
                        return value
    return None


def has_endpoint_url_field_with_default_factory(tree):
    """
    Check if AwsEventServiceInjector has an endpoint_url field with a default_factory.
    Returns (found: bool, factory_name: str|None).
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'AwsEventServiceInjector':
            for item in node.body:
                # Check for annotated assignment with Field
                if isinstance(item, ast.AnnAssign):
                    target_name = None
                    if isinstance(item.target, ast.Name):
                        target_name = item.target.id
                    if target_name == 'endpoint_url' and item.value is not None:
                        # Check if it uses Field with default_factory
                        if isinstance(item.value, ast.Call):
                            func_name = None
                            if isinstance(item.value.func, ast.Name):
                                func_name = item.value.func.id
                            if func_name == 'Field':
                                # Look for default_factory keyword
                                for keyword in item.value.keywords:
                                    if keyword.arg == 'default_factory':
                                        factory_name = None
                                        if isinstance(keyword.value, ast.Name):
                                            factory_name = keyword.value.id
                                        return True, factory_name
    return False, None


# =============================================================================
# Fail-to-Pass Tests (Verify the fix works)
# These tests check BEHAVIOR by executing the endpoint URL logic
# =============================================================================


class TestEndpointUrlBehavior:
    """Test cases for endpoint URL field behavior - implementation agnostic."""

    def test_endpoint_url_logic_exists(self):
        """There exists logic to compute endpoint URL from env vars (f2p)."""
        tree = parse_ast()
        assert tree is not None, "Could not parse target file"

        logic_func = get_endpoint_url_logic(tree)
        assert logic_func is not None,             "Must have logic that reads AWS_S3_ENDPOINT and AWS_S3_SECURE env vars"

    def test_no_env_vars_returns_none(self, monkeypatch):
        """The endpoint logic returns None when no env vars set (f2p)."""
        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        tree = parse_ast()
        assert tree is not None, "Target file must exist"

        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found - fix not applied yet")

        result = logic_func()
        assert result is None, f"Expected None when no env vars set, got {result}"

    def test_endpoint_with_https_prefix_secure(self, monkeypatch):
        """Endpoint URL with https:// prefix when secure=true (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_endpoint_without_prefix_secure_adds_https(self, monkeypatch):
        """Adds https:// prefix when secure=true and no protocol (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_endpoint_with_http_prefix_insecure(self, monkeypatch):
        """Endpoint URL with http:// prefix when secure=false (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'http://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'false')

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_endpoint_without_prefix_insecure_adds_http(self, monkeypatch):
        """Adds http:// prefix when secure=false and no protocol (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'false')

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_endpoint_http_converted_to_https_when_secure(self, monkeypatch):
        """Converts http:// to https:// when secure=true (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'http://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000, got {result}"

    def test_endpoint_https_converted_to_http_when_insecure(self, monkeypatch):
        """Converts https:// to http:// when secure=false (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'false')

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'http://minio.example.com:9000', f"Expected http://minio.example.com:9000, got {result}"

    def test_secure_defaults_to_true(self, monkeypatch):
        """AWS_S3_SECURE defaults to true when not set (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'minio.example.com:9000')
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        tree = parse_ast()
        logic_func = get_endpoint_url_logic(tree)
        if logic_func is None:
            pytest.skip("Endpoint URL logic not found")

        result = logic_func()
        assert result == 'https://minio.example.com:9000', f"Expected https://minio.example.com:9000 (default secure), got {result}"


class TestAwsEventServiceInjectorEndpointUrl:
    """Test cases for AwsEventServiceInjector endpoint_url field."""

    def test_injector_has_endpoint_url_field_with_default_factory(self):
        """AwsEventServiceInjector has endpoint_url field with default_factory (f2p)."""
        tree = parse_ast()
        assert tree is not None, "Could not parse target file"

        has_field, factory_name = has_endpoint_url_field_with_default_factory(tree)
        assert has_field,             "AwsEventServiceInjector must have endpoint_url field with Field(default_factory=...)"

    def test_endpoint_url_factory_reads_env(self, monkeypatch):
        """The default_factory for endpoint_url reads from env vars (f2p)."""
        monkeypatch.setenv('AWS_S3_ENDPOINT', 'https://minio.example.com:9000')
        monkeypatch.setenv('AWS_S3_SECURE', 'true')

        tree = parse_ast()
        has_field, factory_name = has_endpoint_url_field_with_default_factory(tree)

        if not has_field:
            pytest.skip("endpoint_url field with default_factory not found")

        # Find and execute the factory function
        factory_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == factory_name:
                module = ast.Module(body=[node], type_ignores=[])
                module = ast.fix_missing_locations(module)
                code = compile(module, '<string>', 'exec')
                namespace = {'os': os}
                exec(code, namespace)
                factory_func = namespace.get(factory_name)
                break

        if factory_func is None:
            pytest.skip(f"Factory function {factory_name} not found")

        result = factory_func()
        assert result == 'https://minio.example.com:9000',             f"Factory should return URL from env, got {result}"

    def test_endpoint_url_factory_returns_none_when_no_env(self, monkeypatch):
        """The default_factory returns None when AWS_S3_ENDPOINT not set (f2p)."""
        monkeypatch.delenv('AWS_S3_ENDPOINT', raising=False)
        monkeypatch.delenv('AWS_S3_SECURE', raising=False)

        tree = parse_ast()
        has_field, factory_name = has_endpoint_url_field_with_default_factory(tree)

        if not has_field:
            pytest.skip("endpoint_url field with default_factory not found")

        # Find and execute the factory function
        factory_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == factory_name:
                module = ast.Module(body=[node], type_ignores=[])
                module = ast.fix_missing_locations(module)
                code = compile(module, '<string>', 'exec')
                namespace = {'os': os}
                exec(code, namespace)
                factory_func = namespace.get(factory_name)
                break

        if factory_func is None:
            pytest.skip(f"Factory function {factory_name} not found")

        result = factory_func()
        assert result is None, f"Factory should return None when no env var, got {result}"


class TestEndpointUrlUsedInS3Client:
    """Test that endpoint_url is actually used when creating S3 client."""

    def test_s3_client_uses_self_endpoint_url(self):
        """S3 client creation uses self.endpoint_url not os.getenv (f2p)."""
        source = read_source_code()
        assert source is not None, "Target file must exist"

        # The fix removes the direct os.getenv call in favor of self.endpoint_url
        # This test verifies the fix is applied by checking the source code pattern
        assert "os.getenv('AWS_S3_ENDPOINT')" not in source,             "S3 client must not use os.getenv('AWS_S3_ENDPOINT') directly - should use self.endpoint_url"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These tests verify that the repo's existing CI checks pass on both
# the base commit and after the fix is applied.
# =============================================================================


def test_repo_python_syntax():
    """Python syntax validation for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

    result = subprocess.run(
        ["python", "-m", "py_compile", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"Python syntax error:\n{result.stderr}"


def test_repo_ast_parses():
    """Python AST parsing for modified file (pass_to_pass)."""
    target_file = get_target_file()
    assert target_file.exists(), f"Target file not found: {target_file}"

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

    result = subprocess.run(
        [
            "bash",
            "-c",
            "pip install ruff -q && ruff check --config dev_config/python/ruff.toml --fix openhands/app_server/event/aws_event_service.py && ruff check --config dev_config/python/ruff.toml openhands/app_server/event/aws_event_service.py",
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

    content = target_file.read_text()
    assert len(content) > 0, "Target file is empty"
    assert "class AwsEventServiceInjector" in content, "Missing AwsEventServiceInjector class"
    assert "class AwsEventService" in content, "Missing AwsEventService class"
