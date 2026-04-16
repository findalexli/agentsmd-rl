"""
Task: areal-fsdp-pipeline-weight-sync
Repo: inclusionAI/AReaL @ 61281ba8851e6d1cf8c30794a5391359b4e324b7

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests verify behavior via AST analysis and extracted code execution,
NOT via full module imports that go through areal/__init__.py.
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

    Behavioral verification via AST analysis:
    1. A method returns a pending-state object (async dispatch)
    2. A wait method exists to drain pending state
    3. The main loop calls the async method and then the wait method
    """
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

# Find FSDPEngine class
fsdp_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        fsdp_class = node
        break

if fsdp_class is None:
    print("FAIL: FSDPEngine not found")
    exit(1)

# Look for a method with 'bucket' and 'weight' in name that has a 'stream' parameter
async_bucket_method = None
wait_method = None

for item in fsdp_class.body:
    if not isinstance(item, ast.FunctionDef):
        continue
    # Check for async bucket method (has 'stream' param, returns something)
    if "bucket" in item.name.lower() and "weight" in item.name.lower():
        all_args = list(item.args.args) + list(item.args.kwonlyargs)
        param_names = [a.arg for a in all_args]
        if "stream" in param_names:
            # Check if the method returns a non-None value
            returns_non_none = False
            for n in ast.walk(item):
                if isinstance(n, ast.Return) and n.value is not None:
                    if not (isinstance(n.value, ast.Constant) and n.value.value is None):
                        returns_non_none = True
            if returns_non_none:
                async_bucket_method = item.name

# Look for a _wait* method that takes a parameter
for item in fsdp_class.body:
    if not isinstance(item, ast.FunctionDef):
        continue
    if "_wait" in item.name.lower() and "bucket" in item.name.lower():
        wait_method = item.name

if async_bucket_method is None:
    print("FAIL: No async bucket method with stream param and return value")
    exit(1)

if wait_method is None:
    print("FAIL: No _wait* bucket method found")
    exit(1)

# Now verify the main loop calls both methods
main_loop_method = None
for item in fsdp_class.body:
    if isinstance(item, ast.FunctionDef) and item.name == "_update_weights_from_distributed":
        main_loop_method = item
        break

if main_loop_method is None:
    print("FAIL: _update_weights_from_distributed not found")
    exit(1)

# Check that it calls the async method and the wait method
calls_async = False
calls_wait = False

for node in ast.walk(main_loop_method):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                if node.func.attr == async_bucket_method:
                    calls_async = True
                if "_wait" in node.func.attr.lower():
                    calls_wait = True

if calls_async and calls_wait:
    print("PASS")
    exit(0)
else:
    print(f"FAIL: main loop calls async={calls_async} wait={calls_wait}")
    exit(1)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_async_bucket_method():
    """Async bucket broadcast method returns pending state with distributed logic.

    Behavioral verification via AST analysis of method structure:
    - Method has 'stream' parameter
    - Method has distributed broadcast with async_op=True
    - Method returns a non-None value
    """
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            # Must have "stream" as a parameter
            all_args = list(item.args.args) + list(item.args.kwonlyargs)
            param_names = [a.arg for a in all_args]
            if "stream" not in param_names:
                continue

            # Must return a non-None value somewhere in the function
            returns_non_none = False
            for n in ast.walk(item):
                if isinstance(n, ast.Return):
                    if n.value is not None:
                        if not (isinstance(n.value, ast.Constant) and n.value.value is None):
                            returns_non_none = True
            if not returns_non_none:
                continue

            # Must have distributed logic (async_op broadcasts)
            has_dist = any(
                isinstance(n, ast.keyword) and n.arg == "async_op"
                for n in ast.walk(item)
            )
            if not has_dist:
                continue

            # Must be substantial (anti-stub)
            meaningful = sum(
                1 for n in ast.walk(item)
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Try, ast.Return, ast.Call))
            )
            if meaningful < 8:
                continue

            # All checks passed
            found = True
            print(f"Found: {item.name} with {meaningful} meaningful nodes")
            break

if found:
    print("PASS")
    exit(0)
else:
    print("FAIL: No async bucket broadcast method with distributed logic found")
    exit(1)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pending_state_dataclass():
    """Data structure with >=3 fields tracks in-flight broadcast state.

    Behavioral verification via AST analysis:
    - A @dataclass exists with 3+ fields including names suggesting handle/future
    - The dataclass is referenced in FSDPEngine code
    """
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

dataclass_classes = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        has_dc = any(
            (isinstance(d, ast.Name) and "dataclass" in d.id)
            or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
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
        if "handle" in f.lower():
            has_handle_type = True
        if "fut" in f.lower():
            has_future_type = True

if not (has_handle_type and has_future_type):
    print("FAIL: Dataclass fields don't suggest handle/future pattern")
    exit(1)

# Verify the dataclass is actually used in the module
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

    Behavioral verification via AST:
    - Main method (_update_weights_from_distributed) has try/finally
    - Finally block calls a self._wait* method
    """
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

has_try_finally = False
has_wait_call = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "_update_weights_from_distributed":
                for child in ast.walk(item):
                    if isinstance(child, ast.Try) and child.finalbody:
                        has_try_finally = True
                        # Check if finally block calls self._wait*
                        for s in ast.walk(ast.Module(body=child.finalbody, type_ignores=[])):
                            if isinstance(s, ast.Call):
                                if isinstance(s.func, ast.Attribute):
                                    if isinstance(s.func.value, ast.Name) and s.func.value.id == "self":
                                        if "_wait" in s.func.attr.lower():
                                            has_wait_call = True

if has_try_finally and has_wait_call:
    print("PASS")
    exit(0)
elif has_try_finally:
    print("FAIL: try/finally exists but no self._wait* call in finally")
    exit(1)
else:
    print("FAIL: No try/finally in _update_weights_from_distributed")
    exit(1)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cuda_stream_usage():
    """CUDA stream used for broadcast overlap in weight update methods.

    Behavioral verification via AST:
    - torch.cuda.Stream() is created somewhere in FSDPEngine
    - The stream is used (passed as argument)
    """
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

stream_created = False
stream_used = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            for child in ast.walk(item):
                # Check for torch.cuda.Stream() call
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr == "Stream":
                        if isinstance(child.func.value, ast.Attribute) and child.func.value.attr == "cuda":
                            stream_created = True
                # Check for stream variable being used (passed as argument)
                if isinstance(child, ast.Name) and child.id in ("stream", "broadcast_stream"):
                    if isinstance(child.ctx, ast.Load):
                        stream_used = True

if stream_created and stream_used:
    print("PASS")
    exit(0)
elif stream_created:
    print("FAIL: Stream created but not used")
    exit(1)
else:
    print("FAIL: No torch.cuda.Stream() creation found")
    exit(1)
""")
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass - regression + anti-stub
# ---------------------------------------------------------------------------


def test_sync_wrapper_preserved():
    """_update_bucket_weights_from_distributed still exists with a real body."""
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "_update_bucket_weights_from_distributed":
                # Check it's not a stub - must have meaningful content
                meaningful = sum(
                    1 for n in ast.walk(item)
                    if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Try, ast.Return, ast.Call))
                )
                if meaningful >= 4:
                    print("PASS")
                    exit(0)

print("FAIL: _update_bucket_weights_from_distributed not found or stubbed")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_init_method_preserved():
    """_init_weight_update_from_distributed still present with real body."""
    r = _run_py("""
import ast

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "FSDPEngine":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "_init_weight_update_from_distributed":
                meaningful = sum(
                    1 for n in ast.walk(item)
                    if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Try, ast.Return, ast.Call))
                )
                if meaningful >= 3:
                    print("PASS")
                    exit(0)

print("FAIL: _init_weight_update_from_distributed not found")
exit(1)
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
