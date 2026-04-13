"""
Task: slime-rollout-make-group-router-params
Repo: THUDM/slime @ 6f11313004dbe71f4194536335b891371eefd0e9

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/slime"
FILE = f"{REPO}/slime/ray/rollout.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# Shared mock/exec infrastructure embedded in subprocess scripts.
# Uses raw string so \n escapes inside the code survive into the subprocess.
_MOCK_INFRA = r'''
import ast, inspect, textwrap
from pathlib import Path

FILE = "/workspace/slime/slime/ray/rollout.py"

def extract_make_group():
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_make_group":
            lines = source.splitlines(keepends=True)
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            func_src = textwrap.dedent("".join(func_lines))
            return func_src, node
    raise AssertionError("_make_group function not found")

def build_exec_namespace(closure_ip="STALE_IP", closure_port=99999):
    captured = []
    class MockServerGroup:
        def __init__(self, **kwargs):
            captured.append(dict(kwargs))
    class MockBox:
        def __getattr__(self, name):
            if name == "hf_checkpoint": return "/fake/model"
            if name == "num_gpus_per_node": return 8
            if name == "offload_rollout": return False
            return MockBox()
    class MockGroupCfg:
        num_gpus_per_engine = 1
        num_gpus = 2
        worker_type = "decode"
        overrides = {}
    class MockLogger:
        def info(self, *a, **kw): pass
        def warning(self, *a, **kw): pass
    ns = {
        "__builtins__": __builtins__,
        "ServerGroup": MockServerGroup,
        "args": MockBox(),
        "pg": None,
        "logger": MockLogger(),
        "router_ip": closure_ip,
        "router_port": closure_port,
        "engine_offset": 0,
        "gpu_offset": 0,
        "rollout_pg_offset": 0,
        "megatron_num_gpus": 0,
    }
    return ns, captured, MockGroupCfg

def get_make_group_fn(func_src, ns):
    tree = ast.parse(func_src)
    nonlocal_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Nonlocal):
            nonlocal_names.extend(node.names)
    if nonlocal_names:
        indented = textwrap.indent(func_src, "    ")
        var_inits = "\n".join(f"    {n} = {ns.get(n, 0)}" for n in nonlocal_names)
        wrapper = f"def _outer_wrapper():\n{var_inits}\n{indented}\n    return _make_group\n"
        exec(wrapper, ns)
        fn = ns["_outer_wrapper"]()
    else:
        exec(func_src, ns)
        fn = ns.get("_make_group")
    assert fn is not None
    return fn

def build_router_kwargs(fn, node, ip, port):
    sig = inspect.signature(fn)
    param_names = list(sig.parameters.keys())
    kw = {}
    for pname in param_names:
        if "router_ip" in pname:
            kw[pname] = ip
        elif "router_port" in pname:
            kw[pname] = port
        elif pname in ("router_config", "router_info"):
            kw[pname] = {"ip": ip, "port": port}
    if node.args.kwarg:
        kw.setdefault("router_ip", ip)
        kw.setdefault("router_port", port)
    return kw
'''


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """rollout.py must parse without syntax errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_make_group_accepts_router_params():
    """_make_group must accept router_ip and router_port as explicit parameters."""
    r = _run_python("""
import ast
from pathlib import Path

source = Path("/workspace/slime/slime/ray/rollout.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_make_group":
        params = [a.arg for a in node.args.args]
        has_router = any("router" in p for p in params)
        assert has_router, f"No router params in {params}"
        print("PASS")
        break
else:
    raise AssertionError("_make_group not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_make_group_uses_param_router_not_closure():
    """When called with explicit router params, ServerGroup receives those values,
    not stale closure values."""
    code = _MOCK_INFRA + """
func_src, node = extract_make_group()
ns, captured, MockGroupCfg = build_exec_namespace(
    closure_ip="CLOSURE_STALE_IP", closure_port=99999
)
fn = get_make_group_fn(func_src, ns)

param_ip = "10.0.0.42"
param_port = 8080
kw = build_router_kwargs(fn, node, param_ip, param_port)
fn(MockGroupCfg(), **kw)

assert len(captured) >= 1, "ServerGroup never constructed"
sg = captured[0]
all_vals = str(sg)
assert param_ip in all_vals and str(param_port) in all_vals, f"Missing param values. Got: {sg}"
assert "CLOSURE_STALE_IP" not in all_vals and "99999" not in all_vals, f"Got closure values. Got: {sg}"
print("PASS")
"""
    r = _run_python(code)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_multi_model_router_independence():
    """Two _make_group calls with different router params produce independent
    ServerGroups (EPD multi-model scenario)."""
    code = _MOCK_INFRA + """
func_src, node = extract_make_group()

model_a_ip, model_a_port = "192.168.1.10", 5000
model_b_ip, model_b_port = "192.168.1.20", 6000

# Closure has model B's values (simulating second loop iteration)
ns, captured, MockGroupCfg = build_exec_namespace(
    closure_ip=model_b_ip, closure_port=model_b_port
)
fn = get_make_group_fn(func_src, ns)

# Call 1: pass model A's router params explicitly
kw_a = build_router_kwargs(fn, node, model_a_ip, model_a_port)
fn(MockGroupCfg(), **kw_a)

# Call 2: pass model B's router params explicitly
ns["engine_offset"] = 0
ns["gpu_offset"] = 0
kw_b = build_router_kwargs(fn, node, model_b_ip, model_b_port)
fn(MockGroupCfg(), **kw_b)

assert len(captured) >= 2, f"Expected 2 constructions, got {len(captured)}"
cap1, cap2 = str(captured[0]), str(captured[1])
assert model_a_ip in cap1 and str(model_a_port) in cap1, f"Call 1 missing A values. Got: {captured[0]}"
assert model_b_ip not in cap1, f"Call 1 has B IP (closure leak). Got: {captured[0]}"
assert model_b_ip in cap2 and str(model_b_port) in cap2, f"Call 2 missing B values. Got: {captured[1]}"
print("PASS")
"""
    r = _run_python(code)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_all_call_sites_pass_router_info():
    """Every _make_group() call inside start_rollout_servers must pass router info."""
    r = _run_python("""
import ast
from pathlib import Path

source = Path("/workspace/slime/slime/ray/rollout.py").read_text()
tree = ast.parse(source)

class CallFinder(ast.NodeVisitor):
    def __init__(self):
        self.calls = []
        self.in_target = False

    def visit_FunctionDef(self, node):
        if node.name == "start_rollout_servers":
            self.in_target = True
            self.generic_visit(node)
            self.in_target = False
        elif self.in_target:
            self.generic_visit(node)

    def visit_Call(self, node):
        if self.in_target and isinstance(node.func, ast.Name) and node.func.id == "_make_group":
            self.calls.append(node)
        self.generic_visit(node)

finder = CallFinder()
finder.visit(tree)

assert len(finder.calls) >= 3, f"Expected >= 3 call sites, found {len(finder.calls)}"

for i, call in enumerate(finder.calls):
    n_pos = len(call.args)
    kw_names = [kw.arg for kw in call.keywords if kw.arg is not None]
    has_router = (
        n_pos >= 2
        or any("router" in (k or "") for k in kw_names)
        or any(kw.arg is None for kw in call.keywords)
    )
    assert has_router, (
        f"Call site {i+1} passes {n_pos} positional arg(s) and keywords "
        f"{kw_names} - no router info"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_rollout_py_syntax():
    """Repo's rollout.py must have valid Python syntax (pass_to_pass)."""
    import ast
    source = Path(FILE).read_text()
    ast.parse(source)


def test_repo_slime_importable():
    """Repo's slime package must be importable (pass_to_pass)."""
    r = _run_python("import slime; print('slime imported successfully')")
    assert r.returncode == 0, f"Failed to import slime: {r.stderr}"


def test_repo_flake8_rollout():
    """Repo's flake8 linter passes on rollout.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-m", "flake8", "slime/ray/rollout.py", "--max-line-length=320", "--extend-ignore=E203"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"flake8 failed:\n{r.stdout}\n{r.stderr}"


def test_repo_pyproject_toml_valid():
    """Repo's pyproject.toml must be valid TOML (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml is invalid:\n{r.stderr}"


def test_repo_setup_py_valid():
    """Repo's setup.py must be valid Python and loadable (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "wheel", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-c", "import ast; ast.parse(open('setup.py').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"setup.py is invalid:\n{r.stderr}"


def test_repo_ruff_check():
    """Repo's ruff linter passes on rollout.py (pass_to_pass).
    Note: B023 (loop variable binding) is ignored as it's the specific bug being fixed."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "slime/ray/rollout.py", "--line-length=320", "--ignore=B023"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_black_check():
    """Repo's black format check passes on rollout.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-m", "black", "--check", "slime/ray/rollout.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"black check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_isort_check():
    """Repo's isort check passes on rollout.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-m", "isort", "--check", "slime/ray/rollout.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_plugin_contracts():
    """Repo's plugin contract tests pass (pass_to_pass)."""
    # Install dependencies required for plugin contract tests
    deps = "numpy packaging pytest pyyaml omegaconf tqdm httpx pybase64 pylatexenc sympy aiohttp"
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install"] + deps.split() + ["-q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/plugin_contracts/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"plugin contract tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_yamllint():
    """Repo's YAML workflow files pass yamllint (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "yamllint", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        [sys.executable, "-m", "yamllint", "-d", "relaxed", ".github/workflows/pre-commit.yml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"yamllint failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

def test_start_rollout_servers_signature():
    """start_rollout_servers must still accept (args, pg) parameters."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "start_rollout_servers":
            params = [a.arg for a in node.args.args]
            assert "args" in params and "pg" in params, (
                f"start_rollout_servers signature changed: {params}"
            )
            return
    raise AssertionError("start_rollout_servers not found")


def test_make_group_not_stub():
    """_make_group must have real logic (not just pass/return)."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_make_group":
            meaningful = [
                s for s in node.body
                if not isinstance(s, ast.Pass)
                and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
            ]
            assert len(meaningful) >= 5, (
                f"_make_group body has only {len(meaningful)} meaningful statements - likely a stub"
            )
            return
    raise AssertionError("_make_group not found")


def test_nonlocal_offset_tracking_preserved():
    """_make_group must still use nonlocal for engine_offset/gpu_offset tracking."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_make_group":
            for child in ast.walk(node):
                if isinstance(child, ast.Nonlocal):
                    if "engine_offset" in child.names or "gpu_offset" in child.names:
                        return
            raise AssertionError("nonlocal offset declaration missing in _make_group")
    raise AssertionError("_make_group not found")
