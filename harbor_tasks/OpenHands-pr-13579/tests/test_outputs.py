"""
Test suite for OpenHands AWS Event Service endpoint URL fix.

This validates that the PR correctly:
1. Adds _get_default_aws_endpoint_url() function
2. Updates AwsEventServiceInjector to use Pydantic Field with default_factory
3. Handles HTTP/HTTPS protocol conversion based on AWS_S3_SECURE env var
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/OpenHands")
SERVICE_FILE = REPO / "openhands" / "app_server" / "event" / "aws_event_service.py"


def test_function_exists_in_source():
    """F2P: _get_default_aws_endpoint_url function exists in source code."""
    source = SERVICE_FILE.read_text()
    tree = ast.parse(source)

    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert "_get_default_aws_endpoint_url" in func_names, \
        "_get_default_aws_endpoint_url function not found in aws_event_service.py"


def test_function_logic():
    """F2P: _get_default_aws_endpoint_url function logic is correct."""
    source = SERVICE_FILE.read_text()
    tree = ast.parse(source)

    # Find the function
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_get_default_aws_endpoint_url":
            func = node
            break

    assert func is not None, "Function not found"

    # Convert function to string and check key patterns
    func_source = ast.unparse(func)

    # Check for os.getenv('AWS_S3_ENDPOINT')
    assert "os.getenv('AWS_S3_ENDPOINT')" in func_source, \
        "Function should read AWS_S3_ENDPOINT from environment"

    # Check for AWS_S3_SECURE handling
    assert "AWS_S3_SECURE" in func_source, \
        "Function should handle AWS_S3_SECURE environment variable"

    # Check for http/https protocol handling
    assert "http://" in func_source or "https://" in func_source, \
        "Function should handle HTTP/HTTPS protocol"

    # Check for secure flag logic
    assert "secure" in func_source.lower(), \
        "Function should have secure flag logic"


def test_injector_has_endpoint_url_field():
    """F2P: AwsEventServiceInjector class has endpoint_url field."""
    source = SERVICE_FILE.read_text()
    tree = ast.parse(source)

    # Find the class
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AwsEventServiceInjector":
            class_node = node
            break

    assert class_node is not None, "AwsEventServiceInjector class not found"

    # Check for endpoint_url in the class body (annotation or Field)
    class_source = ast.unparse(class_node)
    assert "endpoint_url" in class_source, \
        "AwsEventServiceInjector should have endpoint_url field"


def test_injector_uses_pydantic_field():
    """F2P: AwsEventServiceInjector.endpoint_url uses Field with default_factory."""
    source = SERVICE_FILE.read_text()

    # Check for Field import and usage
    assert "from pydantic import Field" in source or "pydantic import Field" in source, \
        "Should import Field from pydantic"

    # Check for default_factory usage with the function
    assert "default_factory=_get_default_aws_endpoint_url" in source, \
        "endpoint_url should use Field with default_factory=_get_default_aws_endpoint_url"


def test_s3_client_uses_self_endpoint_url():
    """F2P: boto3 client uses self.endpoint_url instead of os.getenv."""
    source = SERVICE_FILE.read_text()
    tree = ast.parse(source)

    # Find the inject method and check the s3_client call
    found_self_endpoint = False
    found_os_getenv_in_s3_client = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is boto3.client('s3', ...) call
            if (isinstance(node.func, ast.Attribute) and
                node.func.attr == 'client' and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'boto3'):

                # Check keyword arguments
                for kw in node.keywords:
                    if kw.arg == 'endpoint_url':
                        # Check if it's using self.endpoint_url
                        if isinstance(kw.value, ast.Attribute):
                            if (kw.value.attr == 'endpoint_url' and
                                isinstance(kw.value.value, ast.Name) and
                                kw.value.value.id == 'self'):
                                found_self_endpoint = True
                        # Check if it's using os.getenv directly (old code)
                        if isinstance(kw.value, ast.Call):
                            if (isinstance(kw.value.func, ast.Attribute) and
                                kw.value.func.attr == 'getenv' and
                                isinstance(kw.value.func.value, ast.Name) and
                                kw.value.func.value.id == 'os'):
                                found_os_getenv_in_s3_client = True

    assert found_self_endpoint, \
        "S3 client should use self.endpoint_url"
    assert not found_os_getenv_in_s3_client, \
        "S3 client should not use os.getenv('AWS_S3_ENDPOINT') directly"


def test_function_executes_correctly():
    """F2P: _get_default_aws_endpoint_url executes correctly with various env vars."""
    # We'll extract and execute the function to test its behavior
    source = SERVICE_FILE.read_text()
    tree = ast.parse(source)

    # Find the function
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_get_default_aws_endpoint_url":
            func = node
            break

    assert func is not None, "Function not found"

    # Get the function source
    func_source = ast.unparse(func)

    # Execute the function definition in a clean namespace
    namespace = {"os": os}
    exec(func_source, namespace)
    test_func = namespace["_get_default_aws_endpoint_url"]

    # Test 1: No env vars set
    env_backup = {}
    for key in ['AWS_S3_ENDPOINT', 'AWS_S3_SECURE']:
        env_backup[key] = os.environ.pop(key, None)

    try:
        result = test_func()
        assert result is None, f"Expected None when no env vars set, got {result}"

        # Test 2: With HTTPS endpoint and secure=true
        os.environ['AWS_S3_ENDPOINT'] = 'https://minio.example.com:9000'
        os.environ['AWS_S3_SECURE'] = 'true'
        result = test_func()
        assert result == 'https://minio.example.com:9000', \
            f"Expected https://minio.example.com:9000, got {result}"

        # Test 3: No protocol, secure=true -> should add https://
        os.environ['AWS_S3_ENDPOINT'] = 'minio.example.com:9000'
        os.environ['AWS_S3_SECURE'] = 'true'
        result = test_func()
        assert result == 'https://minio.example.com:9000', \
            f"Expected https://minio.example.com:9000, got {result}"

        # Test 4: No protocol, secure=false -> should add http://
        os.environ['AWS_S3_ENDPOINT'] = 'minio.example.com:9000'
        os.environ['AWS_S3_SECURE'] = 'false'
        result = test_func()
        assert result == 'http://minio.example.com:9000', \
            f"Expected http://minio.example.com:9000, got {result}"

        # Test 5: http:// with secure=true -> convert to https://
        os.environ['AWS_S3_ENDPOINT'] = 'http://minio.example.com:9000'
        os.environ['AWS_S3_SECURE'] = 'true'
        result = test_func()
        assert result == 'https://minio.example.com:9000', \
            f"Expected https://minio.example.com:9000, got {result}"

        # Test 6: https:// with secure=false -> convert to http://
        os.environ['AWS_S3_ENDPOINT'] = 'https://minio.example.com:9000'
        os.environ['AWS_S3_SECURE'] = 'false'
        result = test_func()
        assert result == 'http://minio.example.com:9000', \
            f"Expected http://minio.example.com:9000, got {result}"

        # Test 7: secure defaults to true
        os.environ['AWS_S3_ENDPOINT'] = 'minio.example.com:9000'
        del os.environ['AWS_S3_SECURE']
        result = test_func()
        assert result == 'https://minio.example.com:9000', \
            f"Expected https://minio.example.com:9000 (secure default), got {result}"

    finally:
        # Restore environment
        for key, val in env_backup.items():
            if val is not None:
                os.environ[key] = val
            else:
                os.environ.pop(key, None)


def test_pydantic_model_uses_field():
    """F2P: Pydantic Field is imported and used for endpoint_url."""
    source = SERVICE_FILE.read_text()

    # Check that pydantic Field is imported
    assert "from pydantic import Field" in source, \
        "Should import Field from pydantic"

    # Check for Field usage with default_factory
    assert "Field(default_factory=_get_default_aws_endpoint_url)" in source, \
        "Should use Field with default_factory"


def test_file_syntax_valid():
    """P2P: Python file has valid syntax."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SERVICE_FILE)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"aws_event_service.py has syntax errors:\n{result.stderr}"


def test_repo_ruff_lint():
    """Repo's ruff linter passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    # Even if pip has warnings, ruff should be installed
    r = subprocess.run(
        [
            "ruff",
            "check",
            "--config",
            "dev_config/python/ruff.toml",
            "--select",
            "E,W,F,B,ASYNC",
            "openhands/app_server/event/aws_event_service.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    # Only check for critical errors (E, F, W, B, ASYNC), not style issues like I001
    assert r.returncode == 0, f"Ruff found errors:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax():
    """Python syntax validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "openhands/app_server/event/aws_event_service.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Syntax error in aws_event_service.py:\n{r.stderr}"


def test_repo_imports_parseable():
    """Python imports are parseable by AST (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "import ast; ast.parse(open('openhands/app_server/event/aws_event_service.py').read())",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"AST parsing failed:\n{r.stderr}"
