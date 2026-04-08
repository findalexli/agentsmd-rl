"""
Task: areal-cpu-platform-device-fallback
Repo: inclusionAI/AReaL @ 6208006db64ac29aded7be33963e86503ba9e28e
PR:   #1003

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/AReaL"

MODIFIED_FILES = [
    "areal/infra/platforms/cpu.py",
    "areal/engine/fsdp_engine.py",
    "areal/experimental/engine/archon_engine.py",
    "areal/infra/scheduler/local.py",
]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must parse as valid Python."""
    for f in MODIFIED_FILES:
        source = Path(f"{REPO}/{f}").read_text()
        compile(source, f, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Problem 1: CpuPlatform memory methods
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_memory_allocated_and_reserved():
    """CpuPlatform.memory_allocated() and memory_reserved() return 0.

    Behavioral: extracts CpuPlatform via AST, execs with stub Platform base,
    calls methods and asserts return values — all in a subprocess.
    """
    r = _run_py("""
import ast, textwrap
from pathlib import Path

source = Path("areal/infra/platforms/cpu.py").read_text()
tree = ast.parse(source)
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
        class_node = node
        break
assert class_node is not None, "CpuPlatform class not found"

class_src = ast.get_source_segment(source, class_node)
if class_src is None:
    lines = source.splitlines(keepends=True)
    class_src = textwrap.dedent("".join(lines[class_node.lineno - 1 : class_node.end_lineno]))

class Platform:
    pass

ns = {"Platform": Platform, "__builtins__": __builtins__}
exec(class_src, ns)
CpuPlatform = ns["CpuPlatform"]
p = CpuPlatform()

result_a = p.memory_allocated()
assert isinstance(result_a, (int, float)), f"memory_allocated returned {type(result_a)}"
assert result_a == 0, f"memory_allocated should be 0 on CPU, got {result_a}"

result_r = p.memory_reserved()
assert isinstance(result_r, (int, float)), f"memory_reserved returned {type(result_r)}"
assert result_r == 0, f"memory_reserved should be 0 on CPU, got {result_r}"

# Consistency check
assert p.memory_allocated() == 0
assert p.memory_reserved() == 0
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_mem_get_info():
    """CpuPlatform.mem_get_info() returns a 2-tuple of zeros.

    Behavioral: subprocess executes extracted CpuPlatform and calls mem_get_info.
    """
    r = _run_py("""
import ast, textwrap
from pathlib import Path

source = Path("areal/infra/platforms/cpu.py").read_text()
tree = ast.parse(source)
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
        class_node = node
        break
assert class_node is not None

class_src = ast.get_source_segment(source, class_node)
if class_src is None:
    lines = source.splitlines(keepends=True)
    class_src = textwrap.dedent("".join(lines[class_node.lineno - 1 : class_node.end_lineno]))

class Platform:
    pass

ns = {"Platform": Platform, "__builtins__": __builtins__}
exec(class_src, ns)
CpuPlatform = ns["CpuPlatform"]
p = CpuPlatform()

result = p.mem_get_info()
assert isinstance(result, tuple), f"mem_get_info should return tuple, got {type(result)}"
assert len(result) == 2, f"mem_get_info should return 2-tuple, got length {len(result)}"
assert all(isinstance(v, (int, float)) for v in result), f"values should be numeric: {result}"
assert all(v == 0 for v in result), f"mem_get_info should be (0, 0) on CPU, got {result}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_empty_cache():
    """CpuPlatform.empty_cache() is callable and returns None.

    Behavioral: subprocess execs extracted CpuPlatform and verifies empty_cache.
    """
    r = _run_py("""
import ast, textwrap
from pathlib import Path

source = Path("areal/infra/platforms/cpu.py").read_text()
tree = ast.parse(source)
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
        class_node = node
        break
assert class_node is not None

class_src = ast.get_source_segment(source, class_node)
if class_src is None:
    lines = source.splitlines(keepends=True)
    class_src = textwrap.dedent("".join(lines[class_node.lineno - 1 : class_node.end_lineno]))

class Platform:
    pass

ns = {"Platform": Platform, "__builtins__": __builtins__}
exec(class_src, ns)
CpuPlatform = ns["CpuPlatform"]
p = CpuPlatform()

result = p.empty_cache()
assert result is None, f"empty_cache should return None, got {result!r}"
# Call again — idempotent
p.empty_cache()
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Problem 2: device creation respects platform
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fsdp_engine_cpu_device():
    """fsdp_engine._create_device_model creates cpu device when platform is cpu.

    Behavioral: extracts _create_device_model, execs with mock torch/platform
    in a subprocess, checks self.device assignment.
    """
    r = _run_py("""
import ast, textwrap
from pathlib import Path

filepath = "areal/engine/fsdp_engine.py"
source = Path(filepath).read_text()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_create_device_model":
        func_node = node
        break
assert func_node is not None, f"_create_device_model not found in {filepath}"

func_src = ast.get_source_segment(source, func_node)
if func_src is None:
    lines = source.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])
func_src = textwrap.dedent(func_src)

class MockDevice:
    def __init__(self, *args):
        self.args = args
    def __repr__(self):
        return f"device({', '.join(repr(a) for a in self.args)})"

class MockTorch:
    device = MockDevice
    bfloat16 = "bfloat16"
    float16 = "float16"
    float32 = "float32"

class MockPlatform:
    def __init__(self, dt):
        self.device_type = dt
    def set_device(self, *a):
        pass

class Self:
    device = None
    config = type("C", (), {"dtype": "bfloat16", "path": "mock"})()

import types
mock_os = types.SimpleNamespace(environ={"LOCAL_RANK": "0"})

# Test CPU platform
ns = {
    "__builtins__": __builtins__,
    "torch": MockTorch,
    "current_platform": MockPlatform("cpu"),
    "os": mock_os,
}
exec(func_src, ns)
obj = Self()
try:
    ns["_create_device_model"](obj)
except Exception:
    pass
assert obj.device is not None, "self.device was not set (CPU platform)"
assert any(a == "cpu" for a in obj.device.args), (
    f"CPU platform: device should be 'cpu', got device{obj.device.args}"
)

# Test CUDA platform with varying LOCAL_RANK
for rank in ["0", "1", "3"]:
    ns2 = {
        "__builtins__": __builtins__,
        "torch": MockTorch,
        "current_platform": MockPlatform("cuda"),
        "os": types.SimpleNamespace(environ={"LOCAL_RANK": rank}),
    }
    exec(func_src, ns2)
    obj2 = Self()
    try:
        ns2["_create_device_model"](obj2)
    except Exception:
        pass
    assert obj2.device is not None, f"self.device not set for CUDA rank {rank}"
    assert int(rank) in obj2.device.args, (
        f"CUDA rank {rank}: expected device({int(rank)}), got device{obj2.device.args}"
    )

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_archon_engine_cpu_device():
    """archon_engine._create_device_model also handles cpu platform.

    Behavioral: extracts _create_device_model from archon_engine, execs with
    mock torch/platform in a subprocess, checks self.device.
    """
    r = _run_py("""
import ast, textwrap, types
from pathlib import Path

filepath = "areal/experimental/engine/archon_engine.py"
source = Path(filepath).read_text()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_create_device_model":
        func_node = node
        break
assert func_node is not None, f"_create_device_model not found in {filepath}"

func_src = ast.get_source_segment(source, func_node)
if func_src is None:
    lines = source.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])
func_src = textwrap.dedent(func_src)

class MockDevice:
    def __init__(self, *args):
        self.args = args
    def __repr__(self):
        return f"device({', '.join(repr(a) for a in self.args)})"

class MockTorch:
    device = MockDevice
    bfloat16 = "bfloat16"

class MockPlatform:
    def __init__(self, dt):
        self.device_type = dt
    def set_device(self, *a):
        pass

class Self:
    device = None
    config = type("C", (), {"dtype": "bfloat16", "path": "mock"})()

# Test CPU platform
ns = {
    "__builtins__": __builtins__,
    "torch": MockTorch,
    "current_platform": MockPlatform("cpu"),
    "os": types.SimpleNamespace(environ={"LOCAL_RANK": "0"}),
}
exec(func_src, ns)
obj = Self()
try:
    ns["_create_device_model"](obj)
except Exception:
    pass
assert obj.device is not None, "self.device was not set (CPU platform)"
assert any(a == "cpu" for a in obj.device.args), (
    f"CPU platform: device should be 'cpu', got device{obj.device.args}"
)

# Test CUDA platform
for rank in ["0", "2", "5"]:
    ns2 = {
        "__builtins__": __builtins__,
        "torch": MockTorch,
        "current_platform": MockPlatform("cuda"),
        "os": types.SimpleNamespace(environ={"LOCAL_RANK": rank}),
    }
    exec(func_src, ns2)
    obj2 = Self()
    try:
        ns2["_create_device_model"](obj2)
    except Exception:
        pass
    assert obj2.device is not None, f"self.device not set for CUDA rank {rank}"
    assert int(rank) in obj2.device.args, (
        f"CUDA rank {rank}: expected device({int(rank)}), got device{obj2.device.args}"
    )

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Problem 3: scheduler env var guard
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scheduler_guards_env_var():
    """Scheduler must guard device_control_env_var assignment with a conditional.

    Behavioral: subprocess runs AST analysis to verify the guard exists and
    no unguarded assignment remains.
    """
    r = _run_py("""
import ast
from pathlib import Path

source = Path("areal/infra/scheduler/local.py").read_text()
tree = ast.parse(source)

class GuardChecker(ast.NodeVisitor):
    def __init__(self):
        self.guard_depth = 0
        self.found_guarded = False
        self.found_unguarded = False
        self.meaningful_guard = False

    def visit_If(self, node):
        cond_src = ast.get_source_segment(source, node.test) or ""
        relevant = any(
            kw in cond_src
            for kw in ["device_control_env_var", "env_var", "platform"]
        )
        old = self.meaningful_guard
        if relevant:
            self.meaningful_guard = True
        self.guard_depth += 1
        self.generic_visit(node)
        self.guard_depth -= 1
        self.meaningful_guard = old

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                target_src = ast.get_source_segment(source, target) or ""
                if "device_control_env_var" in target_src:
                    if self.guard_depth > 0 and self.meaningful_guard:
                        self.found_guarded = True
                    else:
                        self.found_unguarded = True
        self.generic_visit(node)

checker = GuardChecker()
checker.visit(tree)
assert checker.found_guarded, "device_control_env_var assignment must be inside a conditional"
assert not checker.found_unguarded, (
    "found unguarded device_control_env_var assignment - bug not fixed"
)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_cpu_platform_api():
    """Existing CpuPlatform API preserved (clear_memory, get_visible_devices, attrs)."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path

source = Path("areal/infra/platforms/cpu.py").read_text()
tree = ast.parse(source)
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
        class_node = node
        break
assert class_node is not None

class_src = ast.get_source_segment(source, class_node)
if class_src is None:
    lines = source.splitlines(keepends=True)
    class_src = textwrap.dedent("".join(lines[class_node.lineno - 1 : class_node.end_lineno]))

class Platform:
    pass

ns = {"Platform": Platform, "__builtins__": __builtins__}
exec(class_src, ns)
CpuPlatform = ns["CpuPlatform"]
p = CpuPlatform()

p.clear_memory()  # must not raise
devs = p.get_visible_devices()
assert isinstance(devs, list), f"get_visible_devices should return list, got {type(devs)}"
assert devs == [], f"get_visible_devices should return [], got {devs}"
assert p.device_type == "cpu", f'device_type should be "cpu", got {p.device_type!r}'
assert p.device_control_env_var == "", (
    f'device_control_env_var should be "", got {p.device_control_env_var!r}'
)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md / CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:93, AGENTS.md:30,100 @ 6208006
def test_no_wildcard_imports():
    """No wildcard imports in modified files."""
    for f in MODIFIED_FILES:
        source = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.names:
                for alias in node.names:
                    assert alias.name != "*", f"Wildcard import found in {f}"


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ 6208006
def test_no_bare_print():
    """No bare print() calls in modified files — use areal.utils.logging instead."""
    for f in MODIFIED_FILES:
        source = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    assert False, f"Bare print() call found in {f}:{node.lineno}"


# [agent_config] fail_to_pass — AGENTS.md:99 @ 6208006
def test_new_cpu_methods_have_return_types():
    """New CpuPlatform methods must have explicit return type annotations.

    AGENTS.md:99 requires explicit type hints on new method signatures.
    """
    NEW_METHODS = {"memory_allocated", "memory_reserved", "mem_get_info", "empty_cache"}
    source = Path(f"{REPO}/areal/infra/platforms/cpu.py").read_text()
    tree = ast.parse(source)

    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
            for item in ast.walk(node):
                if isinstance(item, ast.FunctionDef) and item.name in NEW_METHODS:
                    found[item.name] = item.returns

    for method in NEW_METHODS:
        assert method in found, f"CpuPlatform.{method}() not found in cpu.py"
        assert found[method] is not None, (
            f"CpuPlatform.{method}() has no return type annotation (AGENTS.md:99)"
        )
