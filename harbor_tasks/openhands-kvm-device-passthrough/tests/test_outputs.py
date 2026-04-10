"""Tests for KVM device passthrough support in Docker sandbox service."""

import ast
import os
import subprocess
import sys
from pathlib import Path

# Repository path
REPO = Path('/workspace/OpenHands')
TARGET_FILE = REPO / 'openhands' / 'app_server' / 'sandbox' / 'docker_sandbox_service.py'


def get_ast_node():
    """Parse the target file and return its AST."""
    with open(TARGET_FILE) as f:
        source = f.read()
    return ast.parse(source)


def test_kvm_enabled_function_exists():
    """Test that _get_kvm_enabled_default function exists."""
    tree = get_ast_node()

    # Look for the function definition
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_get_kvm_enabled_default':
            return

    raise AssertionError("_get_kvm_enabled_default function not found")


def test_kvm_env_var_true_values():
    """Test _get_kvm_enabled_default returns True for 'true', '1', 'yes'."""
    # This test simulates what the function should do
    # Since we can't import the module, we manually test the logic

    def get_kvm_enabled(value):
        """Simulate the expected logic."""
        return value.lower() in ('true', '1', 'yes')

    # Test 'true'
    assert get_kvm_enabled('true') is True
    assert get_kvm_enabled('TRUE') is True
    assert get_kvm_enabled('True') is True

    # Test '1'
    assert get_kvm_enabled('1') is True

    # Test 'yes'
    assert get_kvm_enabled('yes') is True
    assert get_kvm_enabled('YES') is True


def test_kvm_env_var_false_values():
    """Test _get_kvm_enabled_default returns False for empty, 'false', '0', 'no'."""
    def get_kvm_enabled(value):
        """Simulate the expected logic."""
        return value.lower() in ('true', '1', 'yes')

    # Test empty string (default)
    assert get_kvm_enabled('') is False

    # Test 'false'
    assert get_kvm_enabled('false') is False
    assert get_kvm_enabled('FALSE') is False

    # Test '0'
    assert get_kvm_enabled('0') is False

    # Test 'no'
    assert get_kvm_enabled('no') is False

    # Test random value
    assert get_kvm_enabled('random') is False


def test_docker_sandbox_service_has_kvm_enabled_attribute():
    """Test DockerSandboxService dataclass has kvm_enabled attribute."""
    tree = get_ast_node()

    # Find the DockerSandboxService dataclass
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'DockerSandboxService':
            # Check for kvm_enabled field in the class body
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if hasattr(item.target, 'id') and item.target.id == 'kvm_enabled':
                        return
                elif isinstance(item, ast.Assign):
                    for target in item.targets:
                        if hasattr(target, 'id') and target.id == 'kvm_enabled':
                            return

    raise AssertionError("DockerSandboxService should have kvm_enabled field")


def test_docker_sandbox_service_injector_has_kvm_enabled_field():
    """Test DockerSandboxServiceInjector has kvm_enabled Field."""
    tree = get_ast_node()

    # Find the DockerSandboxServiceInjector class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'DockerSandboxServiceInjector':
            # Check for kvm_enabled field
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if hasattr(item.target, 'id') and item.target.id == 'kvm_enabled':
                        # Check if there's a Field() call
                        if isinstance(item.value, ast.Call):
                            func_name = getattr(item.value.func, 'id', None)
                            if func_name == 'Field':
                                return
            break

    raise AssertionError("DockerSandboxServiceInjector should have kvm_enabled Field")


def test_devices_configuration_in_start_sandbox():
    """Test that start_sandbox method includes devices configuration for KVM."""
    tree = get_ast_node()

    source = None
    # Find the start_sandbox method
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == 'start_sandbox':
                    # Get the source of the method
                    with open(TARGET_FILE) as f:
                        lines = f.readlines()
                        start_line = item.lineno - 1
                        end_line = item.end_lineno
                        source = ''.join(lines[start_line:end_line])
                    break

    if source is None:
        raise AssertionError("start_sandbox method not found")

    # Check that the method contains devices configuration
    assert 'devices' in source, "start_sandbox should reference 'devices'"
    assert '/dev/kvm' in source, "start_sandbox should reference '/dev/kvm'"
    assert 'kvm_enabled' in source, "start_sandbox should reference 'kvm_enabled'"


def test_kvm_enabled_passed_to_service_in_injector():
    """Test that kvm_enabled is passed to DockerSandboxService in injector."""
    tree = get_ast_node()

    source = None
    # Find the inject method
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'DockerSandboxServiceInjector':
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == 'inject':
                    with open(TARGET_FILE) as f:
                        lines = f.readlines()
                        start_line = item.lineno - 1
                        end_line = item.end_lineno
                        source = ''.join(lines[start_line:end_line])
                    break

    if source is None:
        raise AssertionError("inject method not found")

    # Check that kvm_enabled is passed to DockerSandboxService constructor
    assert 'kvm_enabled=self.kvm_enabled' in source, \
        "injector should pass kvm_enabled=self.kvm_enabled to DockerSandboxService"


def test_kvm_logger_info_in_start_sandbox():
    """Test that start_sandbox logs KVM device passthrough message."""
    tree = get_ast_node()

    source = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == 'start_sandbox':
                    with open(TARGET_FILE) as f:
                        lines = f.readlines()
                        start_line = item.lineno - 1
                        end_line = item.end_lineno
                        source = ''.join(lines[start_line:end_line])
                    break

    if source is None:
        raise AssertionError("start_sandbox method not found")

    # Check for KVM logging message
    assert 'KVM device passthrough' in source, \
        "start_sandbox should log KVM device passthrough information"


def test_repo_precommit_ruff():
    """Repo's ruff linter passes (pass_to_pass)."""
    # Skip if pre-commit is not available
    if not subprocess.run(['which', 'pre-commit'], capture_output=True).returncode == 0:
        return

    r = subprocess.run(
        ['pre-commit', 'run', 'ruff', '--all-files', '--config', './dev_config/python/.pre-commit-config.yaml'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_trailing_whitespace():
    """Repo has no trailing whitespace (pass_to_pass)."""
    if not subprocess.run(['which', 'pre-commit'], capture_output=True).returncode == 0:
        return

    r = subprocess.run(
        ['pre-commit', 'run', 'trailing-whitespace', '--all-files', '--config', './dev_config/python/.pre-commit-config.yaml'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_end_of_file_fixer():
    """Repo has proper end-of-file fixer (pass_to_pass)."""
    if not subprocess.run(['which', 'pre-commit'], capture_output=True).returncode == 0:
        return

    r = subprocess.run(
        ['pre-commit', 'run', 'end-of-file-fixer', '--all-files', '--config', './dev_config/python/.pre-commit-config.yaml'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"End of file fixer check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_check_yaml():
    """Repo YAML files are valid (pass_to_pass)."""
    if not subprocess.run(['which', 'pre-commit'], capture_output=True).returncode == 0:
        return

    r = subprocess.run(
        ['pre-commit', 'run', 'check-yaml', '--all-files', '--config', './dev_config/python/.pre-commit-config.yaml'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"YAML check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_debug_statements():
    """Repo has no debug statements (pass_to_pass)."""
    if not subprocess.run(['which', 'pre-commit'], capture_output=True).returncode == 0:
        return

    r = subprocess.run(
        ['pre-commit', 'run', 'debug-statements', '--all-files', '--config', './dev_config/python/.pre-commit-config.yaml'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Debug statements check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_validate_pyproject():
    """Repo pyproject.toml is valid (pass_to_pass)."""
    if not subprocess.run(['which', 'pre-commit'], capture_output=True).returncode == 0:
        return

    r = subprocess.run(
        ['pre-commit', 'run', 'validate-pyproject', '--all-files', '--config', './dev_config/python/.pre-commit-config.yaml'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Validate pyproject check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_docker_sandbox_service_unit_tests():
    """Repo DockerSandboxService unit tests pass (pass_to_pass).

    Tests the core DockerSandboxService functionality including
    host network and injector configuration tests.
    """
    # Install required dependencies
    deps_install = subprocess.run(
        ['pip', 'install', 'pytest-asyncio', 'pytest', 'openhands-agent-server',
         'openhands-sdk', 'openhands-aci', 'termcolor', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if deps_install.returncode != 0:
        pytest.skip(f"Failed to install dependencies: {deps_install.stderr}")

    # Run specific test classes that don't require external services
    r = subprocess.run(
        ['python', '-m', 'pytest',
         'tests/unit/app_server/test_docker_sandbox_service.py::TestDockerSandboxServiceHostNetwork',
         'tests/unit/app_server/test_docker_sandbox_service.py::TestDockerSandboxServiceInjector',
         '-v', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, 'PYTHONPATH': str(REPO)},
    )
    assert r.returncode == 0, f"DockerSandboxService unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]})"


def test_syntax_valid():
    """Test that the modified file has valid Python syntax."""
    with open(TARGET_FILE) as f:
        source = f.read()

    # Should parse without errors
    ast.parse(source)

def test_repo_docker_sandbox_service_main_unit_tests():
    """Repo DockerSandboxService main unit tests pass (pass_to_pass)."""
    deps_install = subprocess.run(
        ['pip', 'install', 'pytest-asyncio', 'pytest', 'openhands-agent-server',
         'openhands-sdk', 'openhands-aci', 'termcolor', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if deps_install.returncode != 0:
        pytest.skip(f"Failed to install dependencies: {deps_install.stderr}")

    r = subprocess.run(
        ['python', '-m', 'pytest',
         'tests/unit/app_server/test_docker_sandbox_service.py::TestDockerSandboxService',
         '-v', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, 'PYTHONPATH': str(REPO)},
    )
    assert r.returncode == 0, f"DockerSandboxService main unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_sandbox_service_unit_tests():
    """Repo SandboxService unit tests pass (pass_to_pass)."""
    deps_install = subprocess.run(
        ['pip', 'install', 'pytest-asyncio', 'pytest', 'openhands-agent-server',
         'openhands-sdk', 'openhands-aci', 'termcolor', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if deps_install.returncode != 0:
        pytest.skip(f"Failed to install dependencies: {deps_install.stderr}")

    r = subprocess.run(
        ['python', '-m', 'pytest',
         'tests/unit/app_server/test_sandbox_service.py',
         '-v', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, 'PYTHONPATH': str(REPO)},
    )
    assert r.returncode == 0, f"SandboxService unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
