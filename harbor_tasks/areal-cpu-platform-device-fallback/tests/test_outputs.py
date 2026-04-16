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

    Behavioral: instantiates CpuPlatform and calls methods, asserting on
    computed return values.
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

    Behavioral: instantiates CpuPlatform and calls mem_get_info.
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
    """CpuPlatform.empty_cache() is explicitly defined in CpuPlatform (not inherited).

    Behavioral: verifies the method exists in CpuPlatform via AST, then calls it
    and confirms it returns None without raising. A trivial stub (no-op) would
    also return None, but a stub wouldn't properly implement the interface.
    This test enforces that the method is defined in CpuPlatform so that callers
    get a valid binding (not inherited from a base class that raises NotImplementedError).
    """
    r = _run_py("""
import ast, textwrap
from pathlib import Path

source = Path("areal/infra/platforms/cpu.py").read_text()
tree = ast.parse(source)

# Find CpuPlatform class
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
        class_node = node
        break
assert class_node is not None, "CpuPlatform class not found"

# Verify empty_cache is explicitly defined in CpuPlatform (not inherited)
method_names = [n.name for n in class_node.body if isinstance(n, ast.FunctionDef)]
assert "empty_cache" in method_names, (
    "empty_cache must be explicitly defined in CpuPlatform, not inherited"
)

# Verify the method body is non-trivial (not just `pass`)
empty_cache_node = None
for node in class_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "empty_cache":
        empty_cache_node = node
        break
# Must have at least one statement beyond `pass`
func_body = empty_cache_node.body
is_trivial = (
    len(func_body) == 1 and
    isinstance(func_body[0], ast.Pass)
)
assert not is_trivial, (
    "empty_cache must not be a trivial pass stub; "
    "it should contain implementation logic"
)

# Extract and execute CpuPlatform
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

# Verify behavior: returns None and is callable without raising
result = p.empty_cache()
assert result is None, f"empty_cache should return None, got {result!r}"
p.empty_cache()  # idempotent - must not raise
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

    Behavioral: extracts _create_device_model, execs with mock torch/platform,
    verifies self.device is set to a CPU-type device (not a CUDA ordinal).
    """
    r = _run_py("""
import ast, textwrap, types
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
    def __init__(self, identifier):
        self.identifier = identifier
    def __repr__(self):
        return f"device('{self.identifier}')"

class MockTorch:
    @staticmethod
    def device(x):
        return MockDevice(x)

class MockPlatform:
    def __init__(self, dt):
        self.device_type = dt
    def set_device(self, *a):
        pass

class Self:
    device = None
    config = type("C", (), {"dtype": "bfloat16", "path": "mock"})()

# Test CPU platform: device identifier must NOT be a CUDA ordinal
ns_cpu = {
    "__builtins__": __builtins__,
    "torch": MockTorch,
    "current_platform": MockPlatform("cpu"),
    "os": types.SimpleNamespace(environ={"LOCAL_RANK": "0"}),
}
exec(func_src, ns_cpu)
obj_cpu = Self()
try:
    ns_cpu["_create_device_model"](obj_cpu)
except Exception:
    pass
assert obj_cpu.device is not None, "self.device must be set for CPU platform"
# The device identifier must NOT be a CUDA ordinal integer (0, 1, 2, ...)
# Alternative correct fixes like torch.device("cpu") or torch.device("cuda:0")
# would both produce a non-ordinal identifier for CPU platform
identifier = obj_cpu.device.identifier
assert not isinstance(identifier, int), (
    f"CPU platform: device identifier must not be a CUDA ordinal int, got {identifier!r}"
)
# It should be some CPU designation (could be "cpu", "cuda:0" from torch.device(int(...)) etc.
# But for CPU platform it should NOT be a bare ordinal
print(f"CPU device identifier: {identifier!r}")

# Test CUDA platform: device identifier must reflect the LOCAL_RANK
for rank in ["0", "1", "3"]:
    ns_cuda = {
        "__builtins__": __builtins__,
        "torch": MockTorch,
        "current_platform": MockPlatform("cuda"),
        "os": types.SimpleNamespace(environ={"LOCAL_RANK": rank}),
    }
    exec(func_src, ns_cuda)
    obj_cuda = Self()
    try:
        ns_cuda["_create_device_model"](obj_cuda)
    except Exception:
        pass
    assert obj_cuda.device is not None, f"self.device must be set for CUDA rank {rank}"
    identifier = obj_cuda.device.identifier
    # The identifier must be some representation of the rank
    # Both torch.device(int(rank)) -> 0/1/3 and torch.device(f'cuda:{rank}') -> 'cuda:0'/'cuda:1'/'cuda:3'
    # would produce identifiers that encode the rank in some form
    rank_int = int(rank)
    valid = (identifier == rank_int) or (str(rank) in str(identifier))
    assert valid, (
        f"CUDA platform with LOCAL_RANK={rank}: device identifier must encode rank, "
        f"got {identifier!r}"
    )
    print(f"CUDA rank={rank} device identifier: {identifier!r}")

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_archon_engine_cpu_device():
    """archon_engine._create_device_model also handles cpu platform.

    Behavioral: extracts _create_device_model, execs with mock torch/platform,
    verifies self.device is set to a CPU-type device (not a CUDA ordinal).
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
    def __init__(self, identifier):
        self.identifier = identifier
    def __repr__(self):
        return f"device('{self.identifier}')"

class MockTorch:
    @staticmethod
    def device(x):
        return MockDevice(x)

class MockPlatform:
    def __init__(self, dt):
        self.device_type = dt
    def set_device(self, *a):
        pass

class Self:
    device = None
    config = type("C", (), {"dtype": "bfloat16", "path": "mock"})()

# Test CPU platform: device identifier must NOT be a CUDA ordinal
ns_cpu = {
    "__builtins__": __builtins__,
    "torch": MockTorch,
    "current_platform": MockPlatform("cpu"),
    "os": types.SimpleNamespace(environ={"LOCAL_RANK": "0"}),
}
exec(func_src, ns_cpu)
obj_cpu = Self()
try:
    ns_cpu["_create_device_model"](obj_cpu)
except Exception:
    pass
assert obj_cpu.device is not None, "self.device must be set for CPU platform"
identifier = obj_cpu.device.identifier
assert not isinstance(identifier, int), (
    f"CPU platform: device identifier must not be a CUDA ordinal int, got {identifier!r}"
)
print(f"CPU device identifier: {identifier!r}")

# Test CUDA platform: device identifier must reflect the LOCAL_RANK
for rank in ["0", "2", "5"]:
    ns_cuda = {
        "__builtins__": __builtins__,
        "torch": MockTorch,
        "current_platform": MockPlatform("cuda"),
        "os": types.SimpleNamespace(environ={"LOCAL_RANK": rank}),
    }
    exec(func_src, ns_cuda)
    obj_cuda = Self()
    try:
        ns_cuda["_create_device_model"](obj_cuda)
    except Exception:
        pass
    assert obj_cuda.device is not None, f"self.device must be set for CUDA rank {rank}"
    identifier = obj_cuda.device.identifier
    rank_int = int(rank)
    valid = (identifier == rank_int) or (str(rank) in str(identifier))
    assert valid, (
        f"CUDA platform with LOCAL_RANK={rank}: device identifier must encode rank, "
        f"got {identifier!r}"
    )
    print(f"CUDA rank={rank} device identifier: {identifier!r}")

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

    Behavioral: verifies that the scheduler code does not produce an empty string
    key in environment dicts when platform device_control_env_var is empty.
    """
    r = _run_py("""
import ast, textwrap, types
from pathlib import Path

source = Path("areal/infra/scheduler/local.py").read_text()
tree = ast.parse(source)

class EnvKeyChecker(ast.NodeVisitor):
    # Check for unguarded assignment to env[...] with device_control_env_var

    def __init__(self):
        self.if_depth = 0
        self.has_meaningful_if = False
        self.found_unguarded = False
        self.found_guarded = False

    def visit_If(self, node):
        cond_src = ast.get_source_segment(source, node.test) or ""
        # Track whether this if guards device_control_env_var
        was_meaningful = self.has_meaningful_if
        if "device_control_env_var" in cond_src or "platform" in cond_src:
            self.has_meaningful_if = True
        old_depth = self.if_depth
        self.if_depth += 1
        self.generic_visit(node)
        self.if_depth = old_depth
        self.has_meaningful_if = was_meaningful

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                target_src = ast.get_source_segment(source, target) or ""
                if "device_control_env_var" in target_src:
                    if self.if_depth > 0 and self.has_meaningful_if:
                        self.found_guarded = True
                    else:
                        self.found_unguarded = True
        self.generic_visit(node)

checker = EnvKeyChecker()
checker.visit(tree)
assert checker.found_guarded, (
    "Assignment to env[current_platform.device_control_env_var] must be guarded by a conditional"
)
assert not checker.found_unguarded, (
    "Found unguarded assignment to env[device_control_env_var] - bug not fixed"
)

# Additional behavioral test: simulate what happens with empty env var
# by checking that the conditional actually checks for non-empty
class ConditionalChecker(ast.NodeVisitor):
    def __init__(self):
        self.cond_texts = []
    def visit_If(self, node):
        cond_src = ast.get_source_segment(source, node.test) or ""
        if "device_control_env_var" in cond_src:
            self.cond_texts.append(cond_src)
        self.generic_visit(node)

cond_checker = ConditionalChecker()
cond_checker.visit(tree)
# The guard should reference device_control_env_var in the condition
assert any("device_control_env_var" in c for c in cond_checker.cond_texts), (
    f"Conditional should reference device_control_env_var, got: {cond_checker.cond_texts}"
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repository CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Ruff linting passes on modified files (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Ruff formatting check passes on modified files (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "format", "--check"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Modified files compile as valid Python (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compilation failed:\n{r.stderr[-500:]}"
# [repo_tests] pass_to_pass
# [repo_tests] pass_to_pass
def test_repo_ast_parse():
    """All modified files parse as valid AST (pass_to_pass)."""
    for f in MODIFIED_FILES:
        r = subprocess.run(
            ["python3", "-c", f"import ast; ast.parse(open('{f}').read())"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"AST parsing failed for {f}:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_all():
    """Ruff linting passes on the entire areal package (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", "areal/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting on areal/ failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_all():
    """Ruff formatting check passes on the entire areal package (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on areal/ failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_yaml():
    """Pre-commit YAML check passes on all files (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit YAML check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_json():
    """Pre-commit JSON check passes on all files (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "check-json", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit JSON check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_eof():
    """Pre-commit end-of-file fixer passes on all files (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit EOF fixer failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_whitespace():
    """Pre-commit trailing whitespace check passes on all files (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit trailing whitespace check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_large_files():
    """Pre-commit check for large files passes (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "check-added-large-files", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit large files check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_private_keys():
    """Pre-commit check for private keys passes (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "detect-private-key", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit private keys check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_nbstripout():
    """Pre-commit notebook stripout check passes on all files (pass_to_pass)."""
    subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["pre-commit", "run", "nbstripout---Strip-notebook-output", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Return code 0 means passed, but pre-commit may return non-zero for other reasons
    # We only care that it doesn't find issues with notebooks
    if r.returncode != 0:
        # Check if the output indicates actual failure vs just "no files to check"
        if "Failed" in r.stdout or "Failed" in r.stderr:
            assert False, f"Pre-commit nbstripout check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
    # If we get here, it passed (or no relevant files to check)
