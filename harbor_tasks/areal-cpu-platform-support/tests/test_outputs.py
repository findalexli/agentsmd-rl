"""
Task: areal-cpu-platform-support
Repo: AReaL @ 6208006db64ac29aded7be33963e86503ba9e28e
PR:   1003

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import logging as stdlib_logging
import re
import sys
import types
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


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
    import ast
    import os
    import textwrap

    import torch

    CpuPlatform = _load_cpu_platform()

    src = Path(f"{REPO}/areal/engine/fsdp_engine.py").read_text()
    tree = ast.parse(src)

    method_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_create_device_model":
            method_src = ast.get_source_segment(src, node)
            break

    assert method_src is not None, "_create_device_model not found in fsdp_engine.py"

    # Execute the method body with a CPU platform mock.
    # The method continues past the device assignment (e.g. dtype, model loading)
    # so we catch AttributeError from missing MockSelf attributes.
    os.environ["LOCAL_RANK"] = "0"
    platform = CpuPlatform()
    # Ensure set_device is a no-op even if torch.cpu lacks it
    platform.set_device = lambda x: None

    class MockSelf:
        pass

    self_obj = MockSelf()

    lines = method_src.split("\n")
    body = "\n".join(lines[1:])  # strip the def line
    body = textwrap.dedent(body)

    try:
        exec(
            compile(body, "<fsdp_create_device_model>", "exec"),
            {
                "self": self_obj,
                "current_platform": platform,
                "os": os,
                "torch": torch,
            },
        )
    except (AttributeError, NameError):
        # Method body references self.config, model loading, etc. that
        # aren't available in the mock — that's fine, we only need the
        # device assignment which happens early.
        pass

    assert hasattr(self_obj, "device"), "device attribute not set by _create_device_model"
    assert self_obj.device == torch.device("cpu"), (
        f"Expected torch.device('cpu'), got {self_obj.device}"
    )


# [pr_diff] fail_to_pass
def test_scheduler_device_env_guard():
    """Scheduler must guard device_control_env_var assignment against empty string."""
    src = Path(f"{REPO}/areal/infra/scheduler/local.py").read_text()

    # The base code unconditionally does:
    #   env[current_platform.device_control_env_var] = ...
    # CpuPlatform has device_control_env_var = "", causing env[""] to be set.
    # A correct fix must guard this assignment.
    assert re.search(r"if\s+.*device_control_env_var", src), (
        "Missing guard: scheduler must check device_control_env_var "
        "is non-empty before setting env key"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------


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
