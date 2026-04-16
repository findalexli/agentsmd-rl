"""
Task: areal-fsdp-optimizer-platform-abstraction
Repo: inclusionAI/AReaL @ cbe35f5a4b866596d996d5690085eda0577708f5
PR:   1108

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/areal/engine/fsdp_utils/optimizer.py"


# ---------------------------------------------------------------------------
# CI Tool Installation (for repo-level pass-to-pass tests)
# ---------------------------------------------------------------------------

def _ensure_ruff():
    """Ensure ruff is installed for linting/formatting checks."""
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, check=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
        env={**__import__("os").environ, "PYTHONPATH": REPO},
    )


def _read_source():
    return Path(FILE).read_text()


def _parse_source():
    source = _read_source()
    tree = ast.parse(source)
    return source, tree


def _find_class_method(tree, source, class_name, method_name):
    """Extract dedented source of a method from a class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    lines = source.splitlines(keepends=True)
                    return textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
    return None


def _find_class_node(tree, class_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """optimizer.py must parse as valid Python."""
    source = _read_source()
    ast.parse(source)


# [repo_ci] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linting passes on optimizer.py (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        ["ruff", "check", FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting check passes on optimizer.py (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        ["ruff", "format", "--check", FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def _ensure_precommit():
    """Ensure pre-commit is installed."""
    try:
        subprocess.run(["pre-commit", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, check=True)


# [repo_ci] pass_to_pass
def test_repo_pre_commit_trailing_whitespace():
    """Repo's pre-commit trailing-whitespace check passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_pre_commit_eof_fixer():
    """Repo's pre-commit end-of-file-fixer check passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"EOF fixer check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_pre_commit_check_yaml():
    """Repo's pre-commit check-yaml check passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Check YAML failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_pre_commit_ruff():
    """Repo's pre-commit ruff linter check passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        ["pre-commit", "run", "ruff", "--all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit ruff check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_pre_commit_ruff_format():
    """Repo's pre-commit ruff-format check passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        ["pre-commit", "run", "ruff-format", "--all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit ruff-format check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_optimizer_ast_valid():
    """optimizer.py AST structure is valid with required classes/methods (pass_to_pass)."""
    code = f"""
import ast
source = open('{FILE}').read()
tree = ast.parse(source)
found_class = False
found_init_streams = False
found_step = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PerLayerOptimWrapper':
        found_class = True
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == '_init_streams_and_events':
                    found_init_streams = True
                elif item.name == 'step':
                    found_step = True
assert found_class, 'PerLayerOptimWrapper class not found'
assert found_init_streams, '_init_streams_and_events method not found'
assert found_step, 'step method not found'
print('AST verification OK')
"""
    r = subprocess.run(
        ["python", "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST validation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_init_streams_behavior():
    """_init_streams_and_events must work without torch.cuda and use platform abstraction.

    We execute the method with a mock platform that fails on torch.cuda calls.
    A correct implementation using platform abstraction will succeed.
    A broken implementation using torch.cuda directly will fail with torch.cuda error.
    """
    r = _run_python('''
import ast, textwrap
from pathlib import Path

source = Path("/repo/areal/engine/fsdp_utils/optimizer.py").read_text()
tree = ast.parse(source)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerLayerOptimWrapper":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "_init_streams_and_events":
                lines = source.splitlines(keepends=True)
                func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
                break

assert func_src is not None, "_init_streams_and_events not found"

# Track whether torch.cuda was accessed
cuda_accessed = []

# Mock platform that succeeds
class _MockPlatform:
    def __getattr__(self, name):
        if name in ("Stream", "Event"):
            def create_mock(**kw):
                class _Obj:
                    def record_event(self, s): pass
                return _Obj()
            return create_mock
        return lambda *a, **kw: None

# Mock torch.cuda that fails on any usage
class _MockTorch:
    class cuda:
        @staticmethod
        def Stream(**kw):
            cuda_accessed.append("Stream")
            raise RuntimeError("torch.cuda not available in this environment")
        @staticmethod
        def Event(**kw):
            cuda_accessed.append("Event")
            raise RuntimeError("torch.cuda not available in this environment")
        @staticmethod
        def current_stream(device):
            cuda_accessed.append("current_stream")
            raise RuntimeError("torch.cuda not available")
        @staticmethod
        def empty_cache():
            cuda_accessed.append("empty_cache")
            raise RuntimeError("torch.cuda not available")
        @staticmethod
        def stream(s):
            cuda_accessed.append("stream")
            raise RuntimeError("torch.cuda not available")

class _MockSelf:
    def __init__(self):
        self._layer_param_groups = [None] * 3
        self.device = "cpu"
        self._h2d_stream = None
        self._d2h_stream = None
        self._compute_end_events = None
        self._h2d_end_events = None

ns = {
    "current_platform": _MockPlatform(),
    "__builtins__": __builtins__,
    "torch": _MockTorch(),
}

try:
    exec(func_src, ns)
    fn = ns["_init_streams_and_events"]
    fn(_MockSelf())
except RuntimeError as e:
    if "torch.cuda" in str(e):
        raise AssertionError(f"Code uses torch.cuda: {e}")
    raise

if cuda_accessed:
    raise AssertionError(f"torch.cuda was accessed: {cuda_accessed}")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_step_behavior():
    """step() must work without torch.cuda and use platform abstraction.

    Execute step() with mock platform. Broken code using torch.cuda will fail.
    Correct code using platform abstraction will succeed.
    """
    r = _run_python('''
import ast, textwrap
from pathlib import Path

source = Path("/repo/areal/engine/fsdp_utils/optimizer.py").read_text()
tree = ast.parse(source)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerLayerOptimWrapper":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "step":
                lines = source.splitlines(keepends=True)
                func_src = textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
                break

assert func_src is not None, "step not found"

cuda_accessed = []

class _Stream:
    def __enter__(self): return self
    def __exit__(self, *args, **kwargs): pass
    def wait_event(self, e): pass
    def record_event(self, s): pass
    def synchronize(self): pass

class _MockEvent:
    def wait_event(self, e): pass
    def record_event(self, s): pass

class _MockSelf:
    def __init__(self):
        self._layer_param_groups = [None] * 3
        self.prefetch_layers = 1
        self.device = "cpu"
        self._h2d_stream = _Stream()
        self._d2h_stream = _Stream()
        self._compute_end_events = [_MockEvent() for _ in range(3)]
        self._h2d_end_events = [_MockEvent() for _ in range(3)]

    def _prefetch_layer(self, idx):
        return {
            "device_p": type("T", (), {"record_stream": lambda *a, **kw: None})(),
            "device_g": type("T", (), {"record_stream": lambda *a, **kw: None})(),
            "device_states": {},
        }

    def _compute_for_layer(self, states):
        pass
    def _offload_layer(self, states):
        pass
    def _record_streams_for_layer(self, states, *streams):
        pass

class _MockPlatform:
    def __getattr__(self, name):
        if name == "stream":
            return lambda s: _Stream()
        elif name == "current_stream":
            return lambda device: _Stream()
        elif name == "empty_cache":
            return lambda: None
        return lambda *a, **kw: None

class _MockTorch:
    class cuda:
        @staticmethod
        def current_stream(device):
            cuda_accessed.append("current_stream")
            raise RuntimeError("torch.cuda not available")
        @staticmethod
        def empty_cache():
            cuda_accessed.append("empty_cache")
            raise RuntimeError("torch.cuda not available")
        @staticmethod
        def stream(s):
            cuda_accessed.append("stream")
            raise RuntimeError("torch.cuda not available")

ns = {
    "current_platform": _MockPlatform(),
    "__builtins__": __builtins__,
    "torch": _MockTorch(),
}

try:
    exec(func_src, ns)
    ns["step"](_MockSelf())
except RuntimeError as e:
    if "torch.cuda" in str(e):
        raise AssertionError(f"step() uses torch.cuda: {e}")
    raise

if cuda_accessed:
    raise AssertionError(f"torch.cuda was accessed in step(): {cuda_accessed}")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_torch_cuda_in_source():
    """PerLayerOptimWrapper source must not contain torch.cuda attribute accesses.

    Uses AST to detect any torch.cuda.X patterns in the class body,
    excluding type annotations.
    """
    r = _run_python('''
import ast
from pathlib import Path

source = Path("/repo/areal/engine/fsdp_utils/optimizer.py").read_text()
tree = ast.parse(source)

class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerLayerOptimWrapper":
        class_node = node
        break
assert class_node is not None, "PerLayerOptimWrapper class not found"

class_source = ast.get_source_segment(source, class_node)
assert class_source is not None
class_tree = ast.parse(class_source)

ann_ids = set()
for child in ast.walk(class_tree):
    if isinstance(child, ast.arg) and child.annotation:
        for n in ast.walk(child.annotation):
            ann_ids.add(id(n))
    if isinstance(child, ast.FunctionDef) and child.returns:
        for n in ast.walk(child.returns):
            ann_ids.add(id(n))
    if isinstance(child, ast.AnnAssign) and child.annotation:
        for n in ast.walk(child.annotation):
            ann_ids.add(id(n))

for n in ast.walk(class_tree):
    if isinstance(n, ast.Attribute) and n.attr in ("Stream", "Event", "current_stream", "stream", "empty_cache"):
        if id(n) in ann_ids:
            continue
        if isinstance(n.value, ast.Attribute) and n.value.attr == "cuda":
            if isinstance(n.value.value, ast.Name) and n.value.value.id == "torch":
                raise AssertionError(f"Found forbidden: torch.cuda.{n.attr}")
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_todo_comments_resolved():
    """TODO comments mentioning platform abstraction must be resolved."""
    source = _read_source()
    for i, line in enumerate(source.splitlines(), 1):
        low = line.lower()
        if "todo" in low and "current_platform" in low:
            raise AssertionError(f"TODO comment at line {i}: {line.strip()}")


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_init_streams_and_events and step must have real logic (not stubbed)."""
    _, tree = _parse_source()
    class_node = _find_class_node(tree, "PerLayerOptimWrapper")
    assert class_node is not None, "PerLayerOptimWrapper class not found"

    for method_name in ("_init_streams_and_events", "step"):
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                meaningful = [
                    s for s in item.body
                    if not isinstance(s, ast.Pass)
                    and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                    and not isinstance(s, ast.Raise)
                ]
                assert len(meaningful) >= 3, (
                    f"{method_name} has only {len(meaningful)} meaningful statements (stubbed)"
                )
                break
        else:
            raise AssertionError(f"{method_name} not found in PerLayerOptimWrapper")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ cbe35f5
def test_no_wildcard_imports():
    """No wildcard imports in optimizer.py (AGENTS.md hard rule)."""
    source = _read_source()
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("from ") and "import *" in stripped:
            raise AssertionError(f"Wildcard import at line {i}: {stripped}")


# [agent_config] pass_to_pass — AGENTS.md:90-92 @ cbe35f5
def test_no_print_statements():
    """No bare print() calls in optimizer.py — must use areal.utils.logging."""
    _, tree = _parse_source()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                raise AssertionError(
                    f"Bare print() call at line {node.lineno} — use areal.utils.logging"
                )


# [agent_config] pass_to_pass — AGENTS.md:96 @ cbe35f5
def test_no_gpu_cpu_sync():
    """No .item() or .tolist() GPU-CPU sync in PerLayerOptimWrapper hot paths."""
    _, tree = _parse_source()
    class_node = _find_class_node(tree, "PerLayerOptimWrapper")
    assert class_node is not None, "PerLayerOptimWrapper class not found"

    forbidden_attrs = {"item", "tolist"}
    for child in ast.walk(class_node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if child.func.attr in forbidden_attrs:
                raise AssertionError(
                    f"GPU-CPU sync .{child.func.attr}() at line {child.lineno}"
                )


# [agent_config] pass_to_pass — AGENTS.md:188-189 @ cbe35f5
def test_no_global_process_groups():
    """No dist.new_group() or dist.init_process_group() at module level in optimizer.py."""
    _, tree = _parse_source()
    forbidden_calls = {"new_group", "init_process_group"}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr in forbidden_calls:
                raise AssertionError(
                    f"Global process group created at module level: "
                    f"{call.func.attr}() at line {node.lineno}"
                )
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            value = node.value if isinstance(node, (ast.Assign, ast.AugAssign)) else node.value
            if value is not None and isinstance(value, ast.Call):
                if (isinstance(value.func, ast.Attribute)
                        and value.func.attr in forbidden_calls):
                    raise AssertionError(
                        f"Global process group created at module level: "
                        f"{value.func.attr}() at line {node.lineno}"
                    )


# [agent_config] pass_to_pass — AGENTS.md:100-101 @ cbe35f5
def test_no_heavy_toplevel_imports():
    """Heavy optional deps must be imported inside functions, not at module level."""
    _, tree = _parse_source()
    heavy_packages = {"transformers", "datasets", "accelerate", "deepspeed", "triton"}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                pkg = alias.name.split(".")[0]
                if pkg in heavy_packages:
                    raise AssertionError(
                        f"Heavy dep '{alias.name}' imported at module level (line {node.lineno})"
                    )
        elif isinstance(node, ast.ImportFrom) and node.module:
            pkg = node.module.split(".")[0]
            if pkg in heavy_packages:
                raise AssertionError(
                    f"Heavy dep '{node.module}' imported at module level (line {node.lineno})"
                    )
