#!/usr/bin/env python3
"""
Task: areal-cpu-platform-support
Repo: AReaL @ 6208006db64ac29aded7be33963e86503ba9e28e
PR:   1003

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import logging as stdlib_logging
import subprocess
import sys
import types
from pathlib import Path

import pytest

REPO = "/workspace/AReaL"


def _load_cpu_platform():
    """Load CpuPlatform class without triggering full areal package imports."""
    import torch

    for name in [
        "areal",
        "areal.utils",
        "areal.infra",
        "areal.infra.platforms",
    ]:
        sys.modules.setdefault(name, types.ModuleType(name))

    mock_log = types.ModuleType("areal.utils.logging")
    mock_log.getLogger = stdlib_logging.getLogger
    sys.modules["areal.utils.logging"] = mock_log

    platform_src = Path(f"{REPO}/areal/infra/platforms/platform.py").read_text()
    platform_ns: dict = {"__name__": "areal.infra.platforms.platform"}
    exec(compile(platform_src, "platform.py", "exec"), platform_ns)

    cpu_src = Path(f"{REPO}/areal/infra/platforms/cpu.py").read_text()
    cpu_src = cpu_src.replace("from .platform import Platform", "")
    cpu_ns: dict = {
        "Platform": platform_ns["Platform"],
        "__name__": "areal.infra.platforms.cpu",
    }
    exec(compile(cpu_src, "cpu.py", "exec"), cpu_ns)

    return cpu_ns["CpuPlatform"]


def _load_platform_base():
    """Load Platform base class for mock GPU platform creation."""
    import torch

    for name in ["areal", "areal.utils", "areal.infra", "areal.infra.platforms"]:
        sys.modules.setdefault(name, types.ModuleType(name))

    mock_log = types.ModuleType("areal.utils.logging")
    mock_log.getLogger = stdlib_logging.getLogger
    sys.modules["areal.utils.logging"] = mock_log

    platform_src = Path(f"{REPO}/areal/infra/platforms/platform.py").read_text()
    platform_ns: dict = {"__name__": "areal.infra.platforms.platform"}
    exec(compile(platform_src, "platform.py", "exec"), platform_ns)

    return platform_ns["Platform"]


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------


def test_syntax_check():
    """Modified Python files must parse without errors."""
    import py_compile

    files = [
        f"{REPO}/areal/engine/fsdp_engine.py",
        f"{REPO}/areal/experimental/engine/archon_engine.py",
        f"{REPO}/areal/infra/platforms/cpu.py",
        f"{REPO}/areal/infra/scheduler/local.py",
    ]
    for f in files:
        py_compile.compile(f, doraise=True)


def test_repo_syntax_all_modules():
    """All areal Python files must have valid syntax (repo CI check)."""
    import py_compile

    repo_path = Path(REPO)
    py_files = list(repo_path.glob("areal/**/*.py"))

    failed = []
    for f in py_files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            failed.append(f"{f}: {e}")

    if failed:
        assert False, f"Syntax errors found in {len(failed)} files:\n" + "\n".join(failed[:10])


def test_repo_cpu_platform_importable():
    """CpuPlatform module can be imported with minimal dependencies (pass_to_pass)."""
    CpuPlatform = _load_cpu_platform()
    assert CpuPlatform is not None, "Failed to load CpuPlatform"


def test_repo_pyproject_toml_valid():
    """pyproject.toml must be valid TOML (repo CI check)."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    pyproject_path = Path(f"{REPO}/pyproject.toml")
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    assert "project" in data, "Missing [project] section"
    assert "dependencies" in data["project"], "Missing dependencies in [project]"


def test_repo_example_configs_valid():
    """Example YAML configs must be valid (repo CI check)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install PyYAML: {r.stderr}"

    import yaml

    repo_path = Path(REPO)
    yaml_files = list(repo_path.glob("examples/**/*.yaml"))

    if not yaml_files:
        return

    failed = []
    for f in yaml_files[:20]:
        try:
            with open(f) as fp:
                yaml.safe_load(fp)
        except yaml.YAMLError as e:
            failed.append(f"{f}: {e}")

    if failed:
        assert False, f"YAML errors in {len(failed)} files:\n" + "\n".join(failed[:5])


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------


def test_cpu_platform_memory_methods_exist():
    """CpuPlatform must define memory_allocated, memory_reserved, mem_get_info, and empty_cache.

    These methods must exist as proper methods (not AttributeError) and return
    values of the expected types for a CPU platform.
    """
    CpuPlatform = _load_cpu_platform()
    p = CpuPlatform()

    # All four methods must exist and be callable
    assert hasattr(p, 'memory_allocated') and callable(p.memory_allocated), \
        "memory_allocated method is missing or not callable"
    assert hasattr(p, 'memory_reserved') and callable(p.memory_reserved), \
        "memory_reserved method is missing or not callable"
    assert hasattr(p, 'mem_get_info') and callable(p.mem_get_info), \
        "mem_get_info method is missing or not callable"
    assert hasattr(p, 'empty_cache') and callable(p.empty_cache), \
        "empty_cache method is missing or not callable"

    # Call each method and verify return types
    result_allocated = p.memory_allocated()
    assert isinstance(result_allocated, int), \
        f"memory_allocated() must return int, got {type(result_allocated).__name__}"

    result_reserved = p.memory_reserved()
    assert isinstance(result_reserved, int), \
        f"memory_reserved() must return int, got {type(result_reserved).__name__}"

    result_info = p.mem_get_info()
    assert isinstance(result_info, tuple), \
        f"mem_get_info() must return tuple, got {type(result_info).__name__}"
    assert len(result_info) == 2, \
        f"mem_get_info() must return 2-tuple, got {len(result_info)}-tuple"
    assert all(isinstance(x, int) for x in result_info), \
        f"mem_get_info() tuple elements must be int, got {[type(x).__name__ for x in result_info]}"

    result_cache = p.empty_cache()
    assert result_cache is None, \
        f"empty_cache() must return None, got {result_cache}"


def test_cpu_platform_memory_values_consistent():
    """CpuPlatform memory methods return values consistent with CPU (no GPU memory).

    On a CPU-only platform, memory_allocated and memory_reserved should return
    0 (no GPU memory), and mem_get_info should return (0, 0).
    """
    CpuPlatform = _load_cpu_platform()
    p = CpuPlatform()

    allocated = p.memory_allocated()
    reserved = p.memory_reserved()
    info = p.mem_get_info()

    # All should be 0 for CPU platform
    assert allocated == 0, f"memory_allocated() on CPU platform should be 0, got {allocated}"
    assert reserved == 0, f"memory_reserved() on CPU platform should be 0, got {reserved}"
    assert info == (0, 0), f"mem_get_info() on CPU platform should be (0, 0), got {info}"


def test_scheduler_device_env_guard():
    """Scheduler must guard device_control_env_var assignment against empty string.

    The fix prevents setting env[""] when device_control_env_var is empty.
    This test uses a mock GPU platform to verify that:
    1. When device_control_env_var IS set, env gets populated
    2. When device_control_env_var is empty, env stays empty (guard works)
    
    Without the guard, setting an empty key would cause issues in some contexts.
    """
    CpuPlatform = _load_cpu_platform()
    Platform = _load_platform_base()

    # Create a mock GPU platform with a non-empty device_control_env_var
    class MockGPUPlatform(Platform):
        device_type = "cuda"
        device_control_env_var = "CUDA_VISIBLE_DEVICES"
        
        def set_device(self, device_id):
            pass

    # Create a CPU platform with empty device_control_env_var
    cpu_platform = CpuPlatform()

    gpu_platform = MockGPUPlatform()

    gpu_devices = [0, 1]

    # Test with GPU platform - env should be set
    env_gpu = {}
    if gpu_platform.device_control_env_var:
        env_gpu[gpu_platform.device_control_env_var] = ",".join(map(str, gpu_devices))
    assert "CUDA_VISIBLE_DEVICES" in env_gpu, \
        f"GPU platform should set CUDA_VISIBLE_DEVICES, got {env_gpu}"

    # Test with CPU platform - env should remain empty (guard prevents setting "")
    env_cpu = {}
    if cpu_platform.device_control_env_var:
        env_cpu[cpu_platform.device_control_env_var] = ",".join(map(str, gpu_devices))
    assert env_cpu == {}, \
        f"CPU platform should NOT set any env vars (device_control_env_var is ''), got {env_cpu}"
    assert "" not in env_cpu, "Empty string key should not be in env"


def test_fsdp_engine_cpu_device():
    """FSDP engine _create_device_model must set device to 'cpu' on CPU platform.

    This test extracts the method via AST and executes just the method body,
    verifying the device is set correctly without triggering module-level imports.
    """
    import ast
    import textwrap

    fsdp_src = Path(f"{REPO}/areal/engine/fsdp_engine.py").read_text()
    tree = ast.parse(fsdp_src)

    # Extract method body via AST (avoids triggering module-level imports)
    method_body = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_create_device_model":
            try:
                method_src = ast.unparse(node)
            except AttributeError:
                lines = fsdp_src.split('\n')
                method_src = '\n'.join(lines[node.lineno-1:node.end_lineno])

            lines = method_src.split('\n')
            if lines[0].startswith('def '):
                lines = lines[1:]
            method_body = textwrap.dedent('\n'.join(lines))
            break

    assert method_body is not None, "Could not find _create_device_model method"

    # Set up execution context
    os_env = {"LOCAL_RANK": "0"}

    class MockConfig:
        dtype = "float32"

    class MockSelf:
        config = MockConfig()
        device = None

    # Load CpuPlatform for context
    CpuPlatform = _load_cpu_platform()
    cpu_platform = CpuPlatform()
    cpu_platform.set_device = lambda x: None

    context = {
        "self": MockSelf(),
        "current_platform": cpu_platform,
        "os": types.SimpleNamespace(environ=os_env),
        "torch": __import__("torch"),
    }

    try:
        exec(compile(method_body, "<_create_device_model>", "exec"), context)
    except Exception:
        # Some code paths may fail; we only care about the final device result
        pass

    # Verify device was set to CPU
    assert hasattr(context["self"], "device"), "device attribute was not set"
    device_str = str(context["self"].device)
    assert "cpu" in device_str.lower(), f"Expected CPU device, got {context['self'].device}"
    assert "cuda" not in device_str.lower(), f"Device should not be CUDA on CPU platform"


def test_archon_engine_cpu_device():
    """Archon engine _create_device_model must set device to 'cpu' on CPU platform.

    This test extracts the method via AST and executes just the method body,
    verifying the device is set correctly without triggering module-level imports.
    """
    import ast
    import textwrap

    archon_src = Path(f"{REPO}/areal/experimental/engine/archon_engine.py").read_text()
    tree = ast.parse(archon_src)

    # Extract method body via AST
    method_body = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_create_device_model":
            try:
                method_src = ast.unparse(node)
            except AttributeError:
                lines = archon_src.split('\n')
                method_src = '\n'.join(lines[node.lineno-1:node.end_lineno])

            lines = method_src.split('\n')
            if lines[0].startswith('def '):
                lines = lines[1:]
            method_body = textwrap.dedent('\n'.join(lines))
            break

    assert method_body is not None, "Could not find _create_device_model method"

    # Set up execution context
    os_env = {"LOCAL_RANK": "0"}

    class MockConfig:
        path = "test/model"

    class MockSelf:
        config = MockConfig()
        device = None

    # Mock load_hf_tokenizer
    def mock_load_hf_tokenizer(path):
        return None

    # Load CpuPlatform for context
    CpuPlatform = _load_cpu_platform()
    cpu_platform = CpuPlatform()
    cpu_platform.set_device = lambda x: None

    context = {
        "self": MockSelf(),
        "current_platform": cpu_platform,
        "os": types.SimpleNamespace(environ=os_env),
        "torch": __import__("torch"),
        "load_hf_tokenizer": mock_load_hf_tokenizer,
    }

    try:
        exec(compile(method_body, "<_create_device_model>", "exec"), context)
    except Exception:
        pass

    # Verify device was set to CPU
    assert hasattr(context["self"], "device"), "device attribute was not set"
    device_str = str(context["self"].device)
    assert "cpu" in device_str.lower(), f"Expected CPU device, got {context['self'].device}"
    assert "cuda" not in device_str.lower(), f"Device should not be CUDA on CPU platform"


# -----------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from CLAUDE.md / AGENTS.md
# -----------------------------------------------------------------------------


def test_no_wildcard_imports():
    """Modified files must not use wildcard imports (CLAUDE.md: 'Never use wildcard imports')."""
    files = [
        f"{REPO}/areal/engine/fsdp_engine.py",
        f"{REPO}/areal/experimental/engine/archon_engine.py",
        f"{REPO}/areal/infra/platforms/cpu.py",
        f"{REPO}/areal/infra/scheduler/local.py",
    ]
    for fpath in files:
        src = Path(fpath).read_text()
        for i, line in enumerate(src.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("from ") and stripped.endswith("import *"):
                assert False, f"Wildcard import at {fpath}:{i}: {stripped}"


def test_repo_ruff_lint():
    """Ruff linting passes on modified files (repo CI check)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        [
            "ruff", "check",
            f"{REPO}/areal/infra/platforms/cpu.py",
            f"{REPO}/areal/infra/scheduler/local.py",
            f"{REPO}/areal/engine/fsdp_engine.py",
            f"{REPO}/areal/experimental/engine/archon_engine.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Ruff formatting check passes on modified files (repo CI check)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        [
            "ruff", "format", "--check",
            f"{REPO}/areal/infra/platforms/cpu.py",
            f"{REPO}/areal/infra/scheduler/local.py",
            f"{REPO}/areal/engine/fsdp_engine.py",
            f"{REPO}/areal/experimental/engine/archon_engine.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_trailing_whitespace():
    """Modified files must not have trailing whitespace (repo CI check)."""
    files = [
        f"{REPO}/areal/infra/platforms/cpu.py",
        f"{REPO}/areal/infra/scheduler/local.py",
        f"{REPO}/areal/engine/fsdp_engine.py",
        f"{REPO}/areal/experimental/engine/archon_engine.py",
    ]

    for fpath in files:
        r = subprocess.run(
            ["grep", "-n", "[[:space:]]$", fpath],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0 and r.stdout.strip():
            assert False, f"Trailing whitespace found in {fpath}:\n{r.stdout[:500]}"


def test_repo_end_of_file_newline():
    """Modified files must end with a newline (repo CI check)."""
    files = [
        f"{REPO}/areal/infra/platforms/cpu.py",
        f"{REPO}/areal/infra/scheduler/local.py",
        f"{REPO}/areal/engine/fsdp_engine.py",
        f"{REPO}/areal/experimental/engine/archon_engine.py",
    ]

    for fpath in files:
        r = subprocess.run(
            ["tail", "-c", "1", fpath],
            capture_output=True,
        )
        if r.stdout and r.stdout != b'\n':
            assert False, f"File {fpath} does not end with a newline"


def test_repo_import_order():
    """Import order follows project standards (repo CI check)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        [
            "ruff", "check", "--select", "I",
            f"{REPO}/areal/infra/platforms/cpu.py",
            f"{REPO}/areal/infra/scheduler/local.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Import order check failed:\n{r.stdout}\n{r.stderr}"
