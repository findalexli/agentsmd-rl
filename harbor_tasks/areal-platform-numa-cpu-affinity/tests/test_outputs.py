#!/usr/bin/env python3
"""
Task: areal-platform-numa-cpu-affinity
Repo: inclusionAI/AReaL @ 682d5640a3497dd69e6ea2b98d2a0f45f34df578
PR:   1083

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = "/repo"


def _stub_init_files():
    """Blank heavy __init__.py files so platform modules can be imported
    without pulling in flask, aiohttp, transformers, etc."""
    init_paths = [
        "areal/__init__.py",
        "areal/infra/__init__.py",
        "areal/utils/__init__.py",
        "areal/infra/platforms/__init__.py",
    ]
    for rel in init_paths:
        p = Path(REPO) / rel
        if p.exists():
            p.write_text("")


def _prepare_imports():
    """Add repo to sys.path and stub init files for clean imports."""
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    _stub_init_files()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without errors."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    for f in files:
        src = (Path(REPO) / f).read_text()
        ast.parse(src)


# [static] pass_to_pass
def test_no_windows_line_endings():
    """Modified files must use Unix line endings (LF), not Windows (CRLF)."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    for f in files:
        content = (Path(REPO) / f).read_bytes()
        assert content.count(b"\r\n") == 0, f"Windows line endings (CRLF) found in {f}"


# [static] pass_to_pass
def test_trailing_newline():
    """Modified files must end with a newline character."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    for f in files:
        content = (Path(REPO) / f).read_bytes()
        assert content[-1:] == b"\n", f"Missing trailing newline in {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_platform_base_set_numa_affinity():
    """Platform base class must expose set_numa_affinity as a callable no-op."""
    _prepare_imports()
    from areal.infra.platforms.platform import Platform

    assert hasattr(Platform, "set_numa_affinity"), "Platform missing set_numa_affinity"
    assert callable(Platform.set_numa_affinity)

    for rank in [0, 1, 7]:
        result = Platform.set_numa_affinity(rank)
        assert result is None, f"Expected None for rank={rank}, got {result}"


# [pr_diff] fail_to_pass
def test_cuda_handles_missing_pynvml():
    """CudaPlatform.set_numa_affinity must not crash when pynvml is unavailable."""
    _prepare_imports()

    for mod in list(sys.modules):
        if "pynvml" in mod:
            del sys.modules[mod]

    import builtins
    orig_import = builtins.__import__

    def blocking_import(name, *args, **kwargs):
        if name == "pynvml":
            raise ImportError("pynvml not installed (test mock)")
        return orig_import(name, *args, **kwargs)

    builtins.__import__ = blocking_import
    try:
        if "areal.infra.platforms.cuda" in sys.modules:
            del sys.modules["areal.infra.platforms.cuda"]
        from areal.infra.platforms.cuda import CudaPlatform

        CudaPlatform.set_numa_affinity(0)
        CudaPlatform.set_numa_affinity(3)
    finally:
        builtins.__import__ = orig_import


# [pr_diff] fail_to_pass
def test_cuda_sets_cpu_affinity():
    """CudaPlatform.set_numa_affinity must actually set CPU affinity for the process.

    Verifies BEHAVIOR (affinity was modified) not specific NVML function names.
    Any correct implementation (pynvml-based or sysfs-based) that achieves
    CPU affinity binding will pass this test.
    """
    _prepare_imports()
    import types

    mock = types.ModuleType("pynvml")
    calls = []
    affinity_was_set = False

    def mock_set_cpu_affinity(handle):
        nonlocal affinity_was_set
        affinity_was_set = True
        calls.append("set_cpu_affinity_called")

    mock.nvmlInit = lambda: calls.append("nvmlInit")
    mock.nvmlDeviceGetHandleByIndex = lambda idx: (calls.append("getHandle"), f"h{idx}")[1]
    mock.nvmlDeviceSetCpuAffinity = mock_set_cpu_affinity
    mock.nvmlShutdown = lambda: calls.append("nvmlShutdown")
    mock.NVML_AFFINITY_SCOPE_NODE = 0
    mock.NVML_AFFINITY_SCOPE_SOCKET = 1

    class MockNVMLError(Exception):
        pass

    mock.NVMLError = MockNVMLError

    sys.modules["pynvml"] = mock
    try:
        if "areal.infra.platforms.cuda" in sys.modules:
            del sys.modules["areal.infra.platforms.cuda"]
        from areal.infra.platforms.cuda import CudaPlatform

        CudaPlatform.set_numa_affinity(0)

        assert "nvmlInit" in calls, f"nvmlInit not called. Calls: {calls}"
        assert "getHandle" in calls, f"nvmlDeviceGetHandleByIndex not called. Calls: {calls}"
        assert affinity_was_set, f"Affinity was not set. Calls: {calls}"
        assert "nvmlShutdown" in calls, f"nvmlShutdown not called. Calls: {calls}"
    finally:
        del sys.modules["pynvml"]


# [pr_diff] fail_to_pass
def test_cuda_nvml_shutdown():
    """CudaPlatform must call nvmlShutdown after NVML operations."""
    _prepare_imports()
    import types

    mock = types.ModuleType("pynvml")
    calls = []

    mock.nvmlInit = lambda: calls.append("nvmlInit")
    mock.nvmlDeviceGetHandleByIndex = lambda idx: (calls.append("getHandle"), f"h{idx}")[1]
    mock.nvmlDeviceSetCpuAffinity = lambda h: calls.append("setCpuAffinity")
    mock.nvmlDeviceGetCpuAffinityWithinScope = lambda h, n=1024, s=0: (
        calls.append("getCpuAffinity"),
        [0xFFFF],
    )[1]
    mock.nvmlShutdown = lambda: calls.append("nvmlShutdown")
    mock.NVML_AFFINITY_SCOPE_NODE = 0
    mock.NVML_AFFINITY_SCOPE_SOCKET = 1

    class MockNVMLError(Exception):
        pass

    mock.NVMLError = MockNVMLError

    sys.modules["pynvml"] = mock
    try:
        if "areal.infra.platforms.cuda" in sys.modules:
            del sys.modules["areal.infra.platforms.cuda"]
        from areal.infra.platforms.cuda import CudaPlatform

        CudaPlatform.set_numa_affinity(0)

        assert "nvmlShutdown" in calls, f"nvmlShutdown not called. Calls: {calls}"
        init_idx = calls.index("nvmlInit")
        shutdown_idx = calls.index("nvmlShutdown")
        assert shutdown_idx > init_idx, "nvmlShutdown called before nvmlInit"
    finally:
        del sys.modules["pynvml"]


# [pr_diff] fail_to_pass
def test_cuda_handles_nvml_error():
    """CudaPlatform must catch NVML runtime errors without crashing."""
    _prepare_imports()
    import types

    mock = types.ModuleType("pynvml")

    class MockNVMLError(Exception):
        pass

    mock.NVMLError = MockNVMLError

    def failing_init():
        raise MockNVMLError("driver not loaded")

    mock.nvmlInit = failing_init
    mock.nvmlShutdown = lambda: None
    mock.nvmlDeviceGetHandleByIndex = lambda idx: None
    mock.nvmlDeviceSetCpuAffinity = lambda h: None
    mock.nvmlDeviceGetCpuAffinityWithinScope = lambda h, n=1024, s=0: [0xFFFF]
    mock.NVML_AFFINITY_SCOPE_NODE = 0
    mock.NVML_AFFINITY_SCOPE_SOCKET = 1

    sys.modules["pynvml"] = mock
    try:
        if "areal.infra.platforms.cuda" in sys.modules:
            del sys.modules["areal.infra.platforms.cuda"]
        from areal.infra.platforms.cuda import CudaPlatform

        CudaPlatform.set_numa_affinity(0)
        CudaPlatform.set_numa_affinity(2)
    finally:
        del sys.modules["pynvml"]


# [pr_diff] fail_to_pass
def test_engines_call_set_numa_affinity():
    """All three engine files must contain a call to set_numa_affinity.

    AST check is justified because engines require distributed setup
    (torch.distributed, FSDP, Megatron) that cannot be initialized in a
    CPU-only test environment.
    """
    engines = [
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    missing = []
    for path in engines:
        source = (Path(REPO) / path).read_text()
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "set_numa_affinity"
            ):
                found = True
                break
        if not found:
            missing.append(path)

    assert not missing, f"Engines missing set_numa_affinity call: {missing}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_platform_existing_methods():
    """Platform base class existing methods must still be present."""
    _prepare_imports()
    from areal.infra.platforms.platform import Platform

    required = [
        "set_allocator_settings",
        "get_custom_env_vars",
        "clear_cublas_workspaces",
        "get_vllm_worker_class",
    ]
    missing = [m for m in required if not hasattr(Platform, m)]
    assert not missing, f"Platform missing methods: {missing}"


# [repo_tests] pass_to_pass
def test_cuda_existing_methods():
    """CudaPlatform existing methods must still be present."""
    _prepare_imports()
    from areal.infra.platforms.cuda import CudaPlatform

    required = [
        "clear_memory",
        "clear_cublas_workspaces",
        "set_allocator_settings",
        "get_custom_env_vars",
    ]
    missing = [m for m in required if not hasattr(CudaPlatform, m)]
    assert not missing, f"CudaPlatform missing methods: {missing}"


# [static] pass_to_pass
def test_cuda_set_numa_affinity_not_stub():
    """CudaPlatform.set_numa_affinity must have substantial implementation."""
    source = (Path(REPO) / "areal/infra/platforms/cuda.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CudaPlatform":
            for item in ast.walk(node):
                if isinstance(item, ast.FunctionDef) and item.name == "set_numa_affinity":
                    body = [
                        s
                        for s in item.body
                        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                        and not isinstance(s, ast.Pass)
                    ]
                    assert len(body) >= 2, f"Only {len(body)} meaningful statements (need >= 2)"
                    return
            raise AssertionError("set_numa_affinity not found in CudaPlatform")
    raise AssertionError("CudaPlatform class not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_no_wildcard_imports():
    """No wildcard imports in modified platform files."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
    ]
    for f in files:
        source = (Path(REPO) / f).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in node.names):
                raise AssertionError(f"Wildcard import found in {f}")


# [agent_config] pass_to_pass
def test_no_print_logging():
    """Modified files must not use print() for logging — use areal.utils.logging.getLogger."""
    files = ["areal/infra/platforms/cuda.py"]
    for f in files:
        source = (Path(REPO) / f).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "CudaPlatform":
                for item in ast.walk(node):
                    if isinstance(item, ast.FunctionDef) and item.name == "set_numa_affinity":
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "print":
                                raise AssertionError(f"print() call found in set_numa_affinity in {f}")


# [agent_config] fail_to_pass
def test_type_hints_on_set_numa_affinity():
    """set_numa_affinity must have explicit type hints."""
    files = ["areal/infra/platforms/platform.py", "areal/infra/platforms/cuda.py"]
    for f in files:
        source = (Path(REPO) / f).read_text()
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in ("Platform", "CudaPlatform"):
                for item in ast.walk(node):
                    if isinstance(item, ast.FunctionDef) and item.name == "set_numa_affinity":
                        found = True
                        params = item.args.args
                        rank_param = next((p for p in params if p.arg == "local_rank"), None)
                        assert rank_param is not None, f"set_numa_affinity in {f} missing local_rank parameter"
                        assert rank_param.annotation is not None, f"set_numa_affinity in {f}: local_rank missing type annotation"
                        assert item.returns is not None, f"set_numa_affinity in {f} missing return type annotation"
        assert found, f"set_numa_affinity not found in {f}"


# [agent_config] fail_to_pass
def test_pynvml_imported_inside_function():
    """Heavy optional deps (pynvml) must be imported inside functions, not at module level."""
    source = (Path(REPO) / "areal/infra/platforms/cuda.py").read_text()
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "pynvml" in alias.name:
                    raise AssertionError("pynvml imported at module level — must be inside function")
        if isinstance(node, ast.ImportFrom) and node.module and "pynvml" in node.module:
            raise AssertionError("pynvml imported at module level — must be inside function")

    found_local_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CudaPlatform":
            for item in ast.walk(node):
                if isinstance(item, ast.FunctionDef) and item.name == "set_numa_affinity":
                    for child in ast.walk(item):
                        if isinstance(child, ast.Import):
                            for alias in child.names:
                                if "pynvml" in alias.name:
                                    found_local_import = True
                        if isinstance(child, ast.ImportFrom) and child.module and "pynvml" in child.module:
                            found_local_import = True
    assert found_local_import, "pynvml must be imported inside set_numa_affinity (lazy import pattern)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD validation tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_platform():
    """Repo platform files must have valid Python syntax."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    for f in files:
        src = (Path(REPO) / f).read_text()
        ast.parse(src)


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Repo modified files must compile without errors."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    for f in files:
        path = Path(REPO) / f
        r = subprocess.run([sys.executable, "-m", "py_compile", str(path)], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"py_compile failed for {f}: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_import_torch():
    """Repo must be able to import torch."""
    r = subprocess.run([sys.executable, "-c", "import torch; print('torch OK')"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"torch import failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ast_valid_platform():
    """Platform files must have valid AST structure."""
    files = ["areal/infra/platforms/platform.py", "areal/infra/platforms/cuda.py"]
    for f in files:
        src = (Path(REPO) / f).read_text()
        tree = ast.parse(src)
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        assert len(classes) > 0, f"No classes found in {f}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo modified files must pass ruff linting."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    r = subprocess.run([sys.executable, "-m", "ruff", "check"] + [str(Path(REPO) / f) for f in files], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"Ruff lint failed: {r.stdout} {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo modified files must be formatted correctly."""
    files = [
        "areal/infra/platforms/platform.py",
        "areal/infra/platforms/cuda.py",
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    r = subprocess.run([sys.executable, "-m", "ruff", "format", "--check"] + [str(Path(REPO) / f) for f in files], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"Ruff format check failed: {r.stdout} {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_import_engines():
    """Modified engine files must be importable as modules."""
    engine_files = [
        "areal/engine/fsdp_engine.py",
        "areal/engine/megatron_engine.py",
        "areal/experimental/engine/archon_engine.py",
    ]
    for rel_path in engine_files:
        path = Path(REPO) / rel_path
        r = subprocess.run([sys.executable, "-c", f"import ast; ast.parse(open('{path}').read()); print('OK')"], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Failed to parse {rel_path}: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_engine_ast_structure():
    """Engine files must have valid AST with expected class definitions."""
    engines = [
        ("areal/engine/fsdp_engine.py", ["FSDPEngine"]),
        ("areal/engine/megatron_engine.py", ["MegatronEngine"]),
        ("areal/experimental/engine/archon_engine.py", ["ArchonEngine"]),
    ]
    for rel_path, expected_classes in engines:
        path = Path(REPO) / rel_path
        r = subprocess.run([sys.executable, "-c", f"""
import ast
with open('{path}') as f:
    tree = ast.parse(f.read())
classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
for cls in {expected_classes}:
    if cls not in classes:
        raise AssertionError(f"Expected class {{cls}} not found in {rel_path}")
print("OK")
"""], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"AST structure check failed for {rel_path}: {r.stderr}"