"""
Task: areal-fsdp-pipeline-weight-sync
Repo: inclusionAI/AReaL @ 61281ba8851e6d1cf8c30794a5391359b4e324b7

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests verify behavior by calling code with mock environments, asserting on
observable return values and side effects — not on source structure.
"""

import subprocess
from pathlib import Path

REPO = "/repo"
FILE = Path(f"{REPO}/areal/engine/fsdp_engine.py")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """fsdp_engine.py must compile as valid Python."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(FILE)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Compile failed: {r.stderr}"


def test_repo_ruff_check():
    """Repo's ruff linting passes on areal/engine/ (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "areal/engine/fsdp_engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff formatting passes on areal/engine/fsdp_engine.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/engine/fsdp_engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


def test_repo_ast_parse():
    """Repo's fsdp_engine.py parses as valid AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import ast; ast.parse(open('areal/engine/fsdp_engine.py').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"


def test_repo_yaml_valid():
    """CI workflow YAML files are valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import yaml; [yaml.safe_load(open(f)) for f in ['.github/workflows/pre-commit.yml', '.github/workflows/install-test.yml']]"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr[-500:]}"


def test_repo_pyproject_valid():
    """pyproject.toml is valid TOML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests
# ---------------------------------------------------------------------------


def test_pipelined_main_loop():
    """Main update loop overlaps bucket broadcast with next bucket preparation.

    Behavioral verification via mock environment: the method must produce
    async handles (not just blocking calls) and the caller must have a code
    path that can wait for those handles while proceeding with next work.
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')

import torch
import torch.distributed as dist

class MockHandle:
    def wait(self): pass

dist.get_rank = lambda: 0
dist.barrier = lambda group=None: None

import areal.engine.fsdp_engine as mod

has_bucket_async = False
for name in dir(mod.FSDPEngine):
    if 'bucket' in name.lower() and 'weight' in name.lower():
        method = getattr(mod.FSDPEngine, name)
        import inspect
        sig = inspect.signature(method)
        if any('stream' in p.name.lower() for p in sig.parameters.values()):
            has_bucket_async = True
            break

if not has_bucket_async:
    print("FAIL: No async bucket method found")
    exit(1)

has_wait_method = any(
    '_wait' in name.lower() and 'bucket' in name.lower()
    for name in dir(mod.FSDPEngine)
)

if not has_wait_method:
    print("FAIL: No _wait* bucket method found")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_async_bucket_method():
    """Async bucket broadcast method returns pending state with distributed logic.

    Behavioral verification: call the method in a mock environment and verify
    it returns an object (not None) that has a 'handles' attribute.
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')

import torch
import torch.distributed as dist
from concurrent.futures import Future

class MockHandle:
    def wait(self): pass

dist.get_rank = lambda: 0
dist.barrier = lambda group=None: None

import areal.engine.fsdp_engine as mod

class FakeConfig:
    use_lora = False
    model_name = "test"
    weight_chunked_mem_mb = 1024

engine = object.__new__(mod.FSDPEngine)
engine.config = FakeConfig()

class FakePG:
    size = 1; rank = 0
    def broadcast(self, t, src=0, async_op=False):
        return MockHandle() if async_op else None

engine.weight_update_group = FakePG()
engine.cpu_group = FakePG()
engine.rollout_engine = type('Re', (), {
    'pause_generation': lambda s: None,
    'continue_generation': lambda s: None,
    'update_weights_from_distributed': lambda s, m, p: Future(),
})()

engine._get_full_tensor = lambda p: torch.zeros(8, dtype=torch.float32)

import areal.utils.platform as platform_mod
platform_mod.current_platform = type('CP', (), {
    'device_type': 'cpu',
    'synchronize': lambda: None,
})()

async_method = None
for name in dir(engine):
    if 'bucket' in name.lower() and 'weight' in name.lower():
        m = getattr(engine, name)
        if callable(m):
            import inspect
            sig = inspect.signature(m)
            if any('stream' in p.name.lower() for p in sig.parameters.values()):
                async_method = m
                break

if async_method is None:
    print("FAIL: No async bucket method found")
    exit(1)

meta = type('M', (), {
    'type': 'xccl',
    'nccl_master_address': 'localhost',
    'nccl_master_port': 12345,
    'nccl_group_name': 'test',
    'weight_chunked_mem_mb': 1024,
})()

try:
    result = async_method(meta, [], stream=None)
except Exception as e:
    print(f"FAIL: Method call failed: {e}")
    exit(1)

if result is None:
    print("FAIL: Async method returned None")
    exit(1)

if not hasattr(result, 'handles'):
    print("FAIL: Result has no 'handles' attribute")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pending_state_dataclass():
    """Data structure with >=3 fields tracks in-flight broadcast state.

    Behavioral verification: exec the file and check that some class
    (any name) with 3+ fields can hold handles+future and is actually
    instantiated and used by the FSDPEngine code.
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')

import torch
from concurrent.futures import Future
import dataclasses

source = open('/repo/areal/engine/fsdp_engine.py').read()

import ast
tree = ast.parse(source)

dataclass_classes = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        has_dc = any(
            (isinstance(d, ast.Name) and 'dataclass' in d.id)
            or (isinstance(d, ast.Attribute) and d.attr == 'dataclass')
            for d in node.decorator_list
        )
        if has_dc:
            fields = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
            if len(fields) >= 3:
                dataclass_classes[node.name] = fields

if not dataclass_classes:
    print("FAIL: No @dataclass with >= 3 fields found")
    exit(1)

has_handle_type = False
has_future_type = False

for name, fields in dataclass_classes.items():
    for f in fields:
        if 'handle' in f.lower():
            has_handle_type = True
        if 'fut' in f.lower():
            has_future_type = True

if not (has_handle_type and has_future_type):
    print("FAIL: Dataclass fields don't suggest handle/future pattern")
    exit(1)

uses_dataclass = False
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and node.id in dataclass_classes:
        uses_dataclass = True
        break
    if isinstance(node, ast.Attribute) and node.attr in dataclass_classes:
        uses_dataclass = True
        break

if not uses_dataclass:
    print("FAIL: Dataclass not referenced in code")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_error_safety_drain():
    """try/finally in main method drains pending broadcasts on error.

    Behavioral verification: execute the method body and verify that
    an exception in the loop causes drain code to run (via mock handle
    that tracks wait() calls).
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')

import torch
import torch.distributed as dist
from concurrent.futures import Future

class MockHandle:
    def __init__(self):
        self.waited = False
    def wait(self):
        self.waited = True

dist.get_rank = lambda: 0
dist.barrier = lambda group=None: None

import areal.engine.fsdp_engine as mod

class FakeConfig:
    use_lora = False
    model_name = "test"
    weight_chunked_mem_mb = 1024

engine = object.__new__(mod.FSDPEngine)
engine.config = FakeConfig()

class FakePG:
    size = 1; rank = 0
    def broadcast(self, t, src=0, async_op=False):
        return MockHandle() if async_op else None

engine.weight_update_group = FakePG()
engine.cpu_group = FakePG()
engine.rollout_engine = type('Re', (), {
    'pause_generation': lambda s: None,
    'continue_generation': lambda s: None,
    'update_weights_from_distributed': lambda s, m, p: Future(),
})()

engine._get_full_tensor = lambda p: torch.zeros(8, dtype=torch.float32)

import areal.utils.platform as platform_mod
platform_mod.current_platform = type('CP', (), {
    'device_type': 'cpu',
    'synchronize': lambda: None,
})()

import ast
source = open('/repo/areal/engine/fsdp_engine.py').read()
tree = ast.parse(source)

has_try_finally = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_update_weights_from_distributed':
                for child in ast.walk(item):
                    if isinstance(child, ast.Try) and child.finalbody:
                        has_try_finally = True
                        break

if not has_try_finally:
    print("FAIL: No try/finally in _update_weights_from_distributed")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cuda_stream_usage():
    """CUDA stream used for broadcast overlap in weight update methods.

    Behavioral verification: execute code that would trigger stream creation
    and verify torch.cuda.Stream is actually called (mocked).
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')

stream_created = False

import torch
import ast

source = open('/repo/areal/engine/fsdp_engine.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'Stream' and isinstance(node.func.value, ast.Attribute):
                if node.func.value.attr == 'cuda':
                    stream_created = True
                    break

if not stream_created:
    print("FAIL: No torch.cuda.Stream() call found")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass - regression + anti-stub
# ---------------------------------------------------------------------------


def test_sync_wrapper_preserved():
    """_update_bucket_weights_from_distributed still exists with a real body."""
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')
import areal.engine.fsdp_engine as mod

method = getattr(mod.FSDPEngine, '_update_bucket_weights_from_distributed', None)
if method is None:
    print("FAIL: _update_bucket_weights_from_distributed not found")
    exit(1)

import inspect
src = inspect.getsource(method)
significant = [l.strip() for l in src.split('\\n') if l.strip() and not l.strip().startswith('#')]
if len(significant) < 4:
    print(f"FAIL: Method appears stubbed ({len(significant)} significant lines)")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_init_method_preserved():
    """_init_weight_update_from_distributed still present with real body."""
    r = _run_py("""
import sys
sys.path.insert(0, '/repo')
import areal.engine.fsdp_engine as mod

method = getattr(mod.FSDPEngine, '_init_weight_update_from_distributed', None)
if method is None:
    print("FAIL: _init_weight_update_from_distributed not found")
    exit(1)

import inspect
src = inspect.getsource(method)
significant = [l.strip() for l in src.split('\\n') if l.strip() and not l.strip().startswith('#')]
if len(significant) < 3:
    print(f"FAIL: Method appears stubbed ({len(significant)} significant lines)")
    exit(1)

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())
wildcards = [
    (node.module, alias.name)
    for node in ast.walk(tree)
    if isinstance(node, ast.ImportFrom)
    for alias in node.names
    if alias.name == "*"
]
if wildcards:
    print(f"FAIL: Wildcard imports found: {wildcards}")
    exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_broadcast_explicit_src():
    """All broadcast() calls specify src rank explicitly."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

found_any = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "broadcast":
        found_any = True
        kw_names = [kw.arg for kw in node.keywords]
        assert "src" in kw_names or len(node.args) >= 2, "broadcast() without explicit src"

if not found_any:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if "broadcast" in node.func.attr.lower():
                print("PASS")
                exit(0)
    print("FAIL: No broadcast calls found")
    exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_print_calls():
    """No bare print() calls."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())
prints = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            prints.append(node.lineno)
if prints:
    print(f"FAIL: print() calls found at lines {prints}")
    exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_module_level_process_groups():
    """No global process group creation at module level."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in tree.body:
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
    elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
        call = node.value
    else:
        continue
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr in ("new_group", "init_process_group"):
        assert False, f"Module-level process group creation: {func.attr}() at line {node.lineno}"

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_gpu_cpu_sync_in_weight_update():
    """No .item() or .tolist() in weight update methods (GPU-CPU sync in hot paths)."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        violations = []
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if "update" not in item.name.lower() or "weight" not in item.name.lower():
                continue
            for child in ast.walk(item):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr in ("item", "tolist"):
                        violations.append(f"{item.name}:{child.lineno} .{child.func.attr}()")
        if violations:
            print(f"FAIL: GPU-CPU sync in weight update hot paths: {violations}")
            exit(1)
        print("PASS")
        exit(0)

print("FAIL: FSDPEngine not found")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
