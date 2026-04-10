"""
Task: pytorch-inductor-addmm-half-unfuse
Repo: pytorch/pytorch @ bac7b59c6fe3241bb6d6cca89cb4bf1da0662788
PR:   #177144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

torch is NOT installed (too heavy / needs GPU). Tests extract the target
function via AST, exec it with lightweight mocks, and verify behavior
using subprocess.run() for isolation.
"""

import ast
import subprocess
import sys
import textwrap
import types

POST_GRAD = "/workspace/torch/_inductor/fx_passes/post_grad.py"

# Shared inline script for subprocess-based tests — extracts the function,
# mocks torch, and returns whether replacement was attempted for a given dtype.
_SUBPROCESS_TEMPLATE = """\
import ast, sys, textwrap, types

POST_GRAD = {post_grad!r}

class DType:
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return self is other
    def __hash__(self):
        return id(self)
    def __repr__(self):
        return f"torch.{{self.name}}"

torch_mock = types.ModuleType("torch")
torch_mock.bfloat16 = DType("bfloat16")
torch_mock.float16 = DType("float16")
torch_mock.float32 = DType("float32")
torch_mock.float64 = DType("float64")

class MockInp:
    def __init__(self, dtype):
        self.meta = {{"val": type("Val", (), {{"dtype": dtype}})()}}

class MockMatch:
    def __init__(self):
        self.replaced = False
        self.kwargs_data = {{}}
    def replace_by_example(self, *args, **kwargs):
        self.replaced = True
    def __getattr__(self, name):
        return lambda *a, **k: None

with open(POST_GRAD) as f:
    source = f.read()
src_lines = source.splitlines(keepends=True)
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        func_src = textwrap.dedent("".join(src_lines[node.lineno - 1:node.end_lineno]))
        ns = {{
            "torch": torch_mock,
            "Match": type("Match", (), {{}}),
            "V": type("V", (), {{"ops": type("ops", (), {{
                "__getattr__": lambda self, n: lambda *a, **k: None,
            }})()}})(),
            "__builtins__": __builtins__,
        }}
        exec(func_src, ns)
        fn = ns["unfuse_bias_add_to_pointwise"]
        break
else:
    print("FAIL:function_not_found")
    sys.exit(1)

dtype = torch_mock.__dict__[{dtype_name!r}]
match = MockMatch()
result = fn(match, None, None, inp=MockInp(dtype), alpha=1, beta=1)
print(f"replaced={{match.replaced}}")
print(f"result={{result}}")
"""

REPO = "/workspace"


def _run_subprocess(dtype_name: str, timeout: int = 30) -> dict:
    """Run the function extractor in a subprocess for the given dtype name."""
    script = _SUBPROCESS_TEMPLATE.format(
        post_grad=POST_GRAD, dtype_name=dtype_name,
    )
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )
    # Parse output lines into a dict
    output = {}
    for line in r.stdout.strip().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            output[k] = v
    output["_returncode"] = r.returncode
    output["_stderr"] = r.stderr
    return output


# ---------------------------------------------------------------------------
# [static] pass_to_pass
# ---------------------------------------------------------------------------

def test_syntax_check():
    """post_grad.py must parse without syntax errors."""
    with open(POST_GRAD) as f:
        ast.parse(f.read())


# ---------------------------------------------------------------------------
# [pr_diff] fail_to_pass — core behavioral tests (subprocess)
# ---------------------------------------------------------------------------

def test_bfloat16_not_unfused():
    """bfloat16 addmm must NOT be unfused — guard prevents replacement."""
    out = _run_subprocess("bfloat16")
    assert out["_returncode"] == 0, f"Subprocess failed: {out['_stderr']}"
    assert out.get("replaced") == "False", (
        "bfloat16 was not guarded — replacement proceeded (should return early)"
    )


def test_float16_not_unfused():
    """float16 addmm must NOT be unfused — guard prevents replacement."""
    out = _run_subprocess("float16")
    assert out["_returncode"] == 0, f"Subprocess failed: {out['_stderr']}"
    assert out.get("replaced") == "False", (
        "float16 was not guarded — replacement proceeded (should return early)"
    )


def test_guard_returns_early():
    """Guard returns early (None) before replacement logic for both half dtypes."""
    for dtype_name in ("bfloat16", "float16"):
        out = _run_subprocess(dtype_name)
        assert out["_returncode"] == 0, f"{dtype_name} subprocess failed: {out['_stderr']}"
        assert out.get("replaced") == "False", f"{dtype_name} was not guarded"
        assert out.get("result") == "None", (
            f"Expected None return for {dtype_name}, got {out.get('result')}"
        )


# ---------------------------------------------------------------------------
# [pr_diff] pass_to_pass — regression guards (make sure fix isn't over-broad)
# ---------------------------------------------------------------------------

def test_float32_still_unfused():
    """float32 addmm MUST still be unfused (guard is not overbroad)."""
    out = _run_subprocess("float32")
    assert out["_returncode"] == 0, f"Subprocess failed: {out['_stderr']}"
    assert out.get("replaced") == "True", (
        "float32 was incorrectly guarded — replacement did NOT proceed"
    )


def test_float64_still_unfused():
    """float64 addmm MUST still be unfused (guard is not overbroad)."""
    out = _run_subprocess("float64")
    assert out["_returncode"] == 0, f"Subprocess failed: {out['_stderr']}"
    assert out.get("replaced") == "True", (
        "float64 was incorrectly guarded — replacement did NOT proceed"
    )


# ---------------------------------------------------------------------------
# [static] pass_to_pass — anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """unfuse_bias_add_to_pointwise has real logic (>= 3 top-level statements)."""
    with open(POST_GRAD) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            count = len(node.body)
            assert count >= 3, f"Only {count} top-level statements — likely a stub"
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")


# ---------------------------------------------------------------------------
# [agent_config] pass_to_pass — rules from agent config files
# ---------------------------------------------------------------------------

# CLAUDE.md:51 @ bac7b59c6fe3241bb6d6cca89cb4bf1da0662788
def test_no_trivial_single_use_helpers():
    """No trivial (1-2 LOC) helper functions introduced that are only used once."""
    with open(POST_GRAD) as f:
        source = f.read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            nested_fns = [n for n in ast.walk(node)
                          if isinstance(n, ast.FunctionDef) and n.name != "unfuse_bias_add_to_pointwise"]
            for fn_node in nested_fns:
                body_stmts = [s for s in fn_node.body
                              if not isinstance(s, (ast.Pass, ast.Expr))
                              or (isinstance(s, ast.Expr) and not isinstance(s.value, ast.Constant))]
                if fn_node.name == "repl":
                    continue
                if len(body_stmts) <= 2:
                    usages = sum(1 for n2 in ast.walk(node)
                                 if isinstance(n2, ast.Call)
                                 and isinstance(getattr(n2, 'func', None), ast.Name)
                                 and n2.func.id == fn_node.name)
                    assert usages > 1, (
                        f"Trivial helper '{fn_node.name}' ({len(body_stmts)} stmts) "
                        f"is only used {usages} time(s)"
                    )
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")


# .claude/skills/pr-review/bc-guidelines.md:46-48 @ bac7b59c6fe3241bb6d6cca89cb4bf1da0662788
def test_python310_compat():
    """Modified function must be Python 3.10 compatible (no except* syntax)."""
    with open(POST_GRAD) as f:
        source = f.read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            for child in ast.walk(node):
                if hasattr(ast, 'TryStar') and isinstance(child, ast.TryStar):
                    raise AssertionError("except* (ExceptionGroup) syntax requires Python 3.11+")
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")


# CLAUDE.md:53-56 @ bac7b59c6fe3241bb6d6cca89cb1da0662788
def test_no_dynamic_attr_access():
    """unfuse_bias_add_to_pointwise must not use dynamic setattr/getattr for state management."""
    with open(POST_GRAD) as f:
        source = f.read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    if isinstance(func, ast.Name) and func.id in ("setattr", "getattr"):
                        raise AssertionError(
                            f"Dynamic {func.id}() used in unfuse_bias_add_to_pointwise"
                        )
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")


# ---------------------------------------------------------------------------
# [repo_tests] pass_to_pass — repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_flake8():
    """Repo's Python linting (flake8) passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install flake8: {r.stderr[-500:]}"
    r = subprocess.run(
        ["flake8", POST_GRAD],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"flake8 failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_ruff():
    """Repo's Python linting (ruff) passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"
    r = subprocess.run(
        ["ruff", "check", POST_GRAD],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_python_syntax():
    """Modified file compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", POST_GRAD],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


def test_repo_bandit():
    """Security linting (bandit) passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "bandit", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install bandit: {r.stderr[-500:]}"
    r = subprocess.run(
        ["bandit", POST_GRAD, "-ll", "-ii", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"bandit found security issues:\n{r.stdout[-500:]}{r.stderr[-500:]}"
