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
    """Load CpuPlatform class without triggering full areal package imports.

    The areal.__init__.py imports heavy dependencies (peft, torchdata,
    transformers, etc.) that are not installed in the test image.  We stub
    out the package hierarchy and load only platform.py + cpu.py via exec().
    """
    import torch  # noqa: F401 — needed by platform.py at exec time

    # Stub the areal package tree so `import areal.utils.logging` inside
    # platform.py resolves without triggering the real __init__.py cascade.
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

    # --- Load Platform base class ---
    platform_src = Path(f"{REPO}/areal/infra/platforms/platform.py").read_text()
    platform_ns: dict = {"__name__": "areal.infra.platforms.platform"}
    exec(compile(platform_src, "platform.py", "exec"), platform_ns)

    # --- Load CpuPlatform (replace relative import with loaded class) ---
    cpu_src = Path(f"{REPO}/areal/infra/platforms/cpu.py").read_text()
    cpu_src = cpu_src.replace("from .platform import Platform", "")
    cpu_ns: dict = {
        "Platform": platform_ns["Platform"],
        "__name__": "areal.infra.platforms.cpu",
    }
    exec(compile(cpu_src, "cpu.py", "exec"), cpu_ns)

    return cpu_ns["CpuPlatform"]


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------


# [static] pass_to_pass
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


# [repo_tests] pass_to_pass - CI-style syntax validation
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


# [repo_tests] pass_to_pass - Platform module import
def test_repo_cpu_platform_importable():
    """CpuPlatform module can be imported with minimal dependencies (pass_to_pass)."""
    # This validates that the CpuPlatform class can be loaded without
    # the full areal dependency chain (which requires many packages).
    CpuPlatform = _load_cpu_platform()
    assert CpuPlatform is not None, "Failed to load CpuPlatform"


# [repo_tests] pass_to_pass - pyproject.toml validation
def test_repo_pyproject_toml_valid():
    """pyproject.toml must be valid TOML (repo CI check)."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Fallback

    pyproject_path = Path(f"{REPO}/pyproject.toml")
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Verify essential sections exist
    assert "project" in data, "Missing [project] section"
    assert "dependencies" in data["project"], "Missing dependencies in [project]"


# [repo_tests] pass_to_pass - YAML config validation
def test_repo_example_configs_valid():
    """Example YAML configs must be valid (repo CI check)."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")

    repo_path = Path(REPO)
    yaml_files = list(repo_path.glob("examples/**/*.yaml"))

    if not yaml_files:
        return  # Skip if no YAML files found

    failed = []
    for f in yaml_files[:20]:  # Limit to first 20 for speed
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


# [pr_diff] fail_to_pass
def test_cpu_platform_memory_allocated():
    """CpuPlatform must implement memory_allocated() returning 0."""
    CpuPlatform = _load_cpu_platform()
    p = CpuPlatform()
    result = p.memory_allocated()
    assert isinstance(result, int), f"Expected int, got {type(result).__name__}"
    assert result == 0, f"Expected 0, got {result}"


# [pr_diff] fail_to_pass
def test_cpu_platform_memory_reserved():
    """CpuPlatform must implement memory_reserved() returning 0."""
    CpuPlatform = _load_cpu_platform()
    p = CpuPlatform()
    result = p.memory_reserved()
    assert isinstance(result, int), f"Expected int, got {type(result).__name__}"
    assert result == 0, f"Expected 0, got {result}"


# [pr_diff] fail_to_pass
def test_cpu_platform_mem_get_info():
    """CpuPlatform must implement mem_get_info() returning a 2-tuple of zeros."""
    CpuPlatform = _load_cpu_platform()
    p = CpuPlatform()
    result = p.mem_get_info()
    assert isinstance(result, tuple), f"Expected tuple, got {type(result).__name__}"
    assert len(result) == 2, f"Expected 2-tuple, got {len(result)}-tuple"
    assert result[0] == 0 and result[1] == 0, f"Expected (0, 0), got {result}"


# [pr_diff] fail_to_pass
def test_cpu_platform_empty_cache():
    """CpuPlatform must implement empty_cache() as a no-op (returns None)."""
    CpuPlatform = _load_cpu_platform()
    p = CpuPlatform()
    result = p.empty_cache()
    assert result is None, f"empty_cache() should return None, got {result}"


# [pr_diff] fail_to_pass
def test_fsdp_engine_cpu_device():
    """FSDP engine _create_device_model must set device to 'cpu' on CPU platform."""
    code = """
import ast
import os
import sys
import textwrap
import types

# Setup minimal module stubs
sys.modules.setdefault('areal', types.ModuleType('areal'))
sys.modules.setdefault('areal.utils', types.ModuleType('areal.utils'))
mock_log = types.ModuleType('areal.utils.logging')
mock_log.getLogger = __import__('logging').getLogger
sys.modules['areal.utils.logging'] = mock_log

import torch

# Load Platform base class
platform_src = open('/workspace/AReaL/areal/infra/platforms/platform.py').read()
platform_ns = {'__name__': 'areal.infra.platforms.platform'}
exec(compile(platform_src, 'platform.py', 'exec'), platform_ns)

# Load CpuPlatform
cpu_src = open('/workspace/AReaL/areal/infra/platforms/cpu.py').read()
cpu_src = cpu_src.replace('from .platform import Platform', '')
cpu_ns = {'Platform': platform_ns['Platform'], '__name__': 'areal.infra.platforms.cpu'}
exec(compile(cpu_src, 'cpu.py', 'exec'), cpu_ns)
CpuPlatform = cpu_ns['CpuPlatform']

# Parse and extract the _create_device_model method
src = open('/workspace/AReaL/areal/engine/fsdp_engine.py').read()
tree = ast.parse(src)

method_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_create_device_model':
        method_src = ast.get_source_segment(src, node)
        break

assert method_src is not None, '_create_device_model not found'

os.environ['LOCAL_RANK'] = '0'
platform = CpuPlatform()
platform.set_device = lambda x: None

class MockSelf:
    pass

self_obj = MockSelf()
lines = method_src.split('\\n')
body = '\\n'.join(lines[1:])
body = textwrap.dedent(body)

try:
    exec(
        compile(body, '<fsdp_create_device_model>', 'exec'),
        {'self': self_obj, 'current_platform': platform, 'os': os, 'torch': torch}
    )
except (AttributeError, NameError):
    pass

assert hasattr(self_obj, 'device'), 'device attribute not set'
assert self_obj.device == torch.device('cpu'), f"Expected cpu, got {self_obj.device}"
print('PASS')
"""

    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_archon_engine_cpu_device():
    """Archon engine _create_device_model must set device to 'cpu' on CPU platform."""
    code = """
import ast
import os
import sys
import textwrap
import types

# Setup minimal module stubs
sys.modules.setdefault('areal', types.ModuleType('areal'))
sys.modules.setdefault('areal.utils', types.ModuleType('areal.utils'))
mock_log = types.ModuleType('areal.utils.logging')
mock_log.getLogger = __import__('logging').getLogger
sys.modules['areal.utils.logging'] = mock_log

import torch

# Load Platform base class
platform_src = open('/workspace/AReaL/areal/infra/platforms/platform.py').read()
platform_ns = {'__name__': 'areal.infra.platforms.platform'}
exec(compile(platform_src, 'platform.py', 'exec'), platform_ns)

# Load CpuPlatform
cpu_src = open('/workspace/AReaL/areal/infra/platforms/cpu.py').read()
cpu_src = cpu_src.replace('from .platform import Platform', '')
cpu_ns = {'Platform': platform_ns['Platform'], '__name__': 'areal.infra.platforms.cpu'}
exec(compile(cpu_src, 'cpu.py', 'exec'), cpu_ns)
CpuPlatform = cpu_ns['CpuPlatform']

# Parse and extract the _create_device_model method from archon_engine
src = open('/workspace/AReaL/areal/experimental/engine/archon_engine.py').read()
tree = ast.parse(src)

method_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_create_device_model':
        method_src = ast.get_source_segment(src, node)
        break

assert method_src is not None, '_create_device_model not found in archon_engine.py'

os.environ['LOCAL_RANK'] = '0'
platform = CpuPlatform()
platform.set_device = lambda x: None

class MockSelf:
    pass

self_obj = MockSelf()
lines = method_src.split('\\n')
body = '\\n'.join(lines[1:])
body = textwrap.dedent(body)

try:
    exec(
        compile(body, '<archon_create_device_model>', 'exec'),
        {'self': self_obj, 'current_platform': platform, 'os': os, 'torch': torch}
    )
except (AttributeError, NameError):
    pass

assert hasattr(self_obj, 'device'), 'device attribute not set by _create_device_model'
assert self_obj.device == torch.device('cpu'), f"Expected torch.device('cpu'), got {self_obj.device}"
print('PASS')
"""

    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_scheduler_device_env_guard():
    """Scheduler must guard device_control_env_var assignment against empty string.

    When current_platform.device_control_env_var is empty (as with CpuPlatform),
    the scheduler must not attempt env[\"\"] assignment which causes a KeyError.
    This test verifies the guard exists and works by executing the relevant code.
    """
    code = '''
import ast
import sys
import textwrap
import types

# Setup minimal module stubs
sys.modules.setdefault('areal', types.ModuleType('areal'))
sys.modules.setdefault('areal.utils', types.ModuleType('areal.utils'))
mock_log = types.ModuleType('areal.utils.logging')
mock_log.getLogger = __import__('logging').getLogger
sys.modules['areal.utils.logging'] = mock_log

# Load Platform base class
platform_src = open('/workspace/AReaL/areal/infra/platforms/platform.py').read()
platform_ns = {'__name__': 'areal.infra.platforms.platform'}
exec(compile(platform_src, 'platform.py', 'exec'), platform_ns)

# Load CpuPlatform
cpu_src = open('/workspace/AReaL/areal/infra/platforms/cpu.py').read()
cpu_src = cpu_src.replace('from .platform import Platform', '')
cpu_ns = {'Platform': platform_ns['Platform'], '__name__': 'areal.infra.platforms.cpu'}
exec(compile(cpu_src, 'cpu.py', 'exec'), cpu_ns)
CpuPlatform = cpu_ns['CpuPlatform']

# Parse scheduler local.py to check the guard exists
src = open('/workspace/AReaL/areal/infra/scheduler/local.py').read()
tree = ast.parse(src)

# Find the create_workers method and check for the guard
found_guard = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'create_workers':
        # Look for an If node that checks device_control_env_var
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check if test involves device_control_env_var
                test_src = ast.get_source_segment(src, child.test)
                if test_src and 'device_control_env_var' in test_src:
                    found_guard = True
                    break
        break

if not found_guard:
    # Fallback: check source text for the pattern
    if 'if current_platform.device_control_env_var:' in src:
        found_guard = True

assert found_guard, 'Missing guard: scheduler must check device_control_env_var is non-empty before setting env key'

# Now test the actual behavior - simulate the env assignment
platform = CpuPlatform()
env = {}
gpu_devices = []

# The buggy code would do: env[platform.device_control_env_var] = ...
# With CpuPlatform, device_control_env_var is "", so this would be env[""] = ...
# Test that the guard prevents this

if platform.device_control_env_var:  # This is the guard pattern
    env[platform.device_control_env_var] = ",".join(map(str, gpu_devices))

# Verify env does not have empty string key
assert "" not in env, 'env should not have empty string key'
print('PASS')
'''

    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# -----------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from CLAUDE.md / AGENTS.md
# -----------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:93 @ 6208006db64ac29aded7be33963e86503ba9e28e
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


# [repo_tests] pass_to_pass - Ruff linting on modified files
def test_repo_ruff_lint():
    """Ruff linting passes on modified files (repo CI check).

    This test runs ruff check on the files modified by the PR to ensure
    they meet the project's linting standards.
    """
    # Install ruff if not available (matches CI version from pyproject.toml)
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


# [repo_tests] pass_to_pass - Ruff format check on modified files
def test_repo_ruff_format():
    """Ruff formatting check passes on modified files (repo CI check).

    This test runs ruff format --check on the files modified by the PR
    to ensure they follow the project's formatting standards.
    """
    # Install ruff if not available (matches CI version from pyproject.toml)
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
