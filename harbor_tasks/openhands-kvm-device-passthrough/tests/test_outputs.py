"""Tests for KVM device passthrough support in DockerSandboxService."""

import os
import subprocess
import sys

# Add the OpenHands directory to the path
REPO = '/workspace/OpenHands'
sys.path.insert(0, REPO)


def test_kvm_enabled_default_function_exists():
    """The _get_kvm_enabled_default function exists and is importable."""
    from openhands.app_server.sandbox.docker_sandbox_service import (
        _get_kvm_enabled_default,
    )

    # Function should be callable with no arguments
    result = _get_kvm_enabled_default()
    assert isinstance(result, bool), "Should return a boolean"


def test_kvm_enabled_function_env_var_true_values():
    """_get_kvm_enabled_default returns True for 'true', '1', 'yes'."""
    from openhands.app_server.sandbox.docker_sandbox_service import (
        _get_kvm_enabled_default,
    )

    true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES']
    for val in true_values:
        os.environ['SANDBOX_KVM_ENABLED'] = val
        result = _get_kvm_enabled_default()
        assert result is True, f"Should return True for '{val}'"
        del os.environ['SANDBOX_KVM_ENABLED']


def test_kvm_enabled_function_env_var_false_values():
    """_get_kvm_enabled_default returns False for empty, 'false', '0', 'no', etc."""
    from openhands.app_server.sandbox.docker_sandbox_service import (
        _get_kvm_enabled_default,
    )

    # Test with no env var set
    if 'SANDBOX_KVM_ENABLED' in os.environ:
        del os.environ['SANDBOX_KVM_ENABLED']
    result = _get_kvm_enabled_default()
    assert result is False, "Should return False when env var not set"

    # Test various false values
    false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', '', 'foo', 'bar']
    for val in false_values:
        os.environ['SANDBOX_KVM_ENABLED'] = val
        result = _get_kvm_enabled_default()
        assert result is False, f"Should return False for '{val}'"
        del os.environ['SANDBOX_KVM_ENABLED']


def test_docker_sandbox_service_has_kvm_enabled_attribute():
    """DockerSandboxService class has kvm_enabled attribute with default False."""
    from openhands.app_server.sandbox.docker_sandbox_service import DockerSandboxService

    # Check that the class has the kvm_enabled attribute in its annotations
    annotations = getattr(DockerSandboxService, '__annotations__', {})
    assert 'kvm_enabled' in annotations, "DockerSandboxService should have kvm_enabled attribute"

    # Check the default value in the class definition
    # The class uses dataclass, so we need to check the default value
    import inspect

    sig = inspect.signature(DockerSandboxService.__init__)
    kvm_param = sig.parameters.get('kvm_enabled')
    assert kvm_param is not None, "kvm_enabled should be a parameter"
    # Default should be False
    assert kvm_param.default is False or str(kvm_param.default) == '<class \'bool\'>', \
        f"kvm_enabled default should be False, got {kvm_param.default}"


def test_device_list_construction_in_start_sandbox():
    """Devices list is correctly constructed based on kvm_enabled flag."""
    # This tests the logic that would be inside start_sandbox
    # We verify the devices list construction pattern exists in the code
    import inspect
    from openhands.app_server.sandbox.docker_sandbox_service import (
        DockerSandboxService,
    )

    source = inspect.getsource(DockerSandboxService.start_sandbox)
    # Check that the devices list construction exists
    assert "devices = " in source, "start_sandbox should define devices variable"
    assert "kvm_enabled" in source, "start_sandbox should reference kvm_enabled"


def test_injector_has_kvm_enabled_field():
    """DockerSandboxServiceInjector has kvm_enabled Field with proper description."""
    from openhands.app_server.sandbox.docker_sandbox_service import (
        DockerSandboxServiceInjector,
    )

    # Check that the class has kvm_enabled attribute
    annotations = getattr(DockerSandboxServiceInjector, '__annotations__', {})
    assert 'kvm_enabled' in annotations, "DockerSandboxServiceInjector should have kvm_enabled"

    # Check the default factory is set correctly
    import inspect
    from pydantic import Field

    sig = inspect.signature(DockerSandboxServiceInjector)
    kvm_param = sig.parameters.get('kvm_enabled')
    assert kvm_param is not None, "kvm_enabled should be a parameter in injector"

    # Check the source for the Field with description
    source = inspect.getsource(DockerSandboxServiceInjector)
    assert "kvm_enabled:" in source or "kvm_enabled =" in source, "kvm_enabled field should exist"
    assert "SANDBOX_KVM_ENABLED" in source, "Field description should mention SANDBOX_KVM_ENABLED"


def test_injector_passes_kvm_enabled_to_service():
    """DockerSandboxServiceInjector passes kvm_enabled to DockerSandboxService."""
    import inspect
    from openhands.app_server.sandbox.docker_sandbox_service import (
        DockerSandboxServiceInjector,
    )

    source = inspect.getsource(DockerSandboxServiceInjector.inject)
    # Check that kvm_enabled is passed when creating DockerSandboxService
    assert "kvm_enabled=self.kvm_enabled" in source, \
        "inject() should pass kvm_enabled=self.kvm_enabled to DockerSandboxService"


def test_devices_parameter_passed_to_docker_run():
    """The devices parameter is passed to docker_client.containers.run()."""
    import inspect
    from openhands.app_server.sandbox.docker_sandbox_service import (
        DockerSandboxService,
    )

    source = inspect.getsource(DockerSandboxService.start_sandbox)
    # Check that devices is passed to containers.run()
    assert "devices=devices" in source, \
        "containers.run() should be called with devices=devices parameter"


def test_file_syntax_valid():
    """The modified Python file has valid syntax (pass_to_pass)."""
    import py_compile

    # Test that the file compiles without syntax errors
    try:
        py_compile.compile(
            '/workspace/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py',
            doraise=True
        )
    except py_compile.PyCompileError as e:
        raise AssertionError(f"Syntax error in docker_sandbox_service.py: {e}")


def test_repo_docker_sandbox_service_unit_tests():
    """Repo's unit tests for docker_sandbox_service pass (pass_to_pass)."""
    # Install pytest-asyncio for async test support
    r = subprocess.run(
        ["pip", "install", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Run the unit tests excluding the ones that need termcolor
    r = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/unit/app_server/test_docker_sandbox_service.py",
            "-v",
            "--ignore-glob=*async*",
            "-k",
            "not test_config_from_env",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_docker_sandbox_service_syntax():
    """Modified docker_sandbox_service.py has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-m",
            "py_compile",
            "openhands/app_server/sandbox/docker_sandbox_service.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"


def test_repo_docker_sandbox_service_imports():
    """DockerSandboxService module imports correctly (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "from openhands.app_server.sandbox.docker_sandbox_service import DockerSandboxService; print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0 and "OK" in r.stdout, f"Import failed:\n{r.stderr[-500:]}"


def test_repo_docker_sandbox_service_injector_tests():
    """DockerSandboxServiceInjector unit tests pass (pass_to_pass)."""
    # Install pytest-asyncio for async test support
    r = subprocess.run(
        ["pip", "install", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Run only the injector tests (excluding env-based ones that need termcolor)
    r = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/unit/app_server/test_docker_sandbox_service.py::TestDockerSandboxServiceInjector",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Injector tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_docker_sandbox_service_volume_mount_tests():
    """VolumeMount and ExposedPort unit tests pass (pass_to_pass)."""
    # Install pytest-asyncio for async test support
    r = subprocess.run(
        ["pip", "install", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Run the VolumeMount and ExposedPort tests
    r = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/unit/app_server/test_docker_sandbox_service.py::TestVolumeMount",
            "tests/unit/app_server/test_docker_sandbox_service.py::TestExposedPort",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"VolumeMount/ExposedPort tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_docker_sandbox_service_host_network_tests():
    """Host network related unit tests pass (pass_to_pass)."""
    # Install pytest-asyncio for async test support
    r = subprocess.run(
        ["pip", "install", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Run the host network tests (similar pattern to kvm_enabled)
    r = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/unit/app_server/test_docker_sandbox_service.py::TestDockerSandboxServiceHostNetwork",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Host network tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
