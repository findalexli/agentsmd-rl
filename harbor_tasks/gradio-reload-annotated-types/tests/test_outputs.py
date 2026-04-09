"""
Task: gradio-reload-annotated-types
Repo: gradio-app/gradio @ c4986883b267570d76b442899c6fc09d14e3e222
PR:   12940

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess

REPO = "/workspace/gradio"
UTILS = f"{REPO}/gradio/utils.py"
SKILLS = f"{REPO}/gradio/cli/commands/skills.py"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with the repo on PYTHONPATH."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_utils_syntax():
    """gradio/utils.py must parse without syntax errors."""
    ast.parse(open(UTILS).read())


# [static] pass_to_pass
def test_skills_syntax():
    """gradio/cli/commands/skills.py must parse without syntax errors."""
    ast.parse(open(SKILLS).read())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_watchfn_no_future_annotations_flag():
    """watchfn code object must not carry CO_FUTURE_ANNOTATIONS flag.

    When utils.py has 'from __future__ import annotations', every function in
    the module inherits CO_FUTURE_ANNOTATIONS. This causes exec() inside
    watchfn to propagate the flag into user code, breaking Annotated types.
    """
    r = _run_python("""
import types, __future__
CO_FLAG = __future__.annotations.compiler_flag
src = open("/workspace/gradio/gradio/utils.py").read()
module_code = compile(src, "utils.py", "exec")
for const in module_code.co_consts:
    if isinstance(const, types.CodeType) and const.co_name == "watchfn":
        has_flag = bool(const.co_flags & CO_FLAG)
        print("HAS_FLAG" if has_flag else "NO_FLAG")
        break
else:
    raise LookupError("No code object named 'watchfn' found")
""")
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    assert "NO_FLAG" in r.stdout, (
        "watchfn still has CO_FUTURE_ANNOTATIONS — "
        "from __future__ import annotations likely still present in utils.py"
    )


# [pr_diff] fail_to_pass
def test_annotated_class_hints_resolve():
    """Annotated class type hints resolve after exec with watchfn's compile flags.

    Simulates the reload path: compile user code using the same flags as
    watchfn, exec it, then call get_type_hints. On the buggy base, the
    inherited CO_FUTURE_ANNOTATIONS flag stringifies annotations, and
    get_type_hints raises on ForwardRef strings.
    """
    r = _run_python(r"""
import types, __future__
from typing import Annotated, get_type_hints

CO_FLAG = __future__.annotations.compiler_flag
src = open("/workspace/gradio/gradio/utils.py").read()
module_code = compile(src, "utils.py", "exec")

watchfn_code = None
for const in module_code.co_consts:
    if isinstance(const, types.CodeType) and const.co_name == "watchfn":
        watchfn_code = const
        break
if watchfn_code is None:
    raise LookupError("No code object named 'watchfn' found")

future_flags = watchfn_code.co_flags & CO_FLAG

user_code = (
    "from typing import Annotated\n"
    "class UserConfig:\n"
    "    name: Annotated[str, 'user name']\n"
    "    count: Annotated[int, 'item count']\n"
    "    flag: Annotated[bool, 'enabled']\n"
)

code = compile(user_code, "<reload>", "exec", flags=future_flags)
ns = {}
exec(code, ns)

hints = get_type_hints(ns["UserConfig"], include_extras=True)
assert hints["name"] == Annotated[str, "user name"], f"Got {hints['name']}"
assert hints["count"] == Annotated[int, "item count"], f"Got {hints['count']}"
print("PASS")
""")
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_annotations_not_stringified_after_exec():
    """Function annotations are real type objects, not strings, after exec.

    When CO_FUTURE_ANNOTATIONS propagates into exec'd code, raw __annotations__
    contain strings instead of actual type objects. This test checks the raw
    annotations directly.
    """
    r = _run_python(r"""
import types, __future__
CO_FLAG = __future__.annotations.compiler_flag
src = open("/workspace/gradio/gradio/utils.py").read()
module_code = compile(src, "utils.py", "exec")

watchfn_code = None
for const in module_code.co_consts:
    if isinstance(const, types.CodeType) and const.co_name == "watchfn":
        watchfn_code = const
        break
if watchfn_code is None:
    raise LookupError("No code object named 'watchfn' found")

future_flags = watchfn_code.co_flags & CO_FLAG

user_code = (
    "from typing import Annotated\n"
    "def process(x: Annotated[str, 'input'], n: Annotated[int, 'repeat']) "
    "-> Annotated[list, 'results']:\n"
    "    return [x] * n\n"
)

code = compile(user_code, "<reload>", "exec", flags=future_flags)
ns = {}
exec(code, ns)

func = ns["process"]
for param_name, ann in func.__annotations__.items():
    assert not isinstance(ann, str), (
        f"Annotation for {param_name!r} is a string {ann!r} — "
        "CO_FUTURE_ANNOTATIONS is leaking into exec'd code"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_forward_refs_are_quoted():
    """Forward-reference annotations (App, Blocks, etc.) must be string literals.

    When 'from __future__ import annotations' is removed, bare references to
    types like App and Blocks (forward refs due to circular imports) would cause
    NameError at import time. The fix must quote them as strings.
    """
    src = open(UTILS).read()
    tree = ast.parse(src)

    forward_ref_names = {"App", "Blocks", "Component", "BlockContext",
                         "Request", "SessionState", "Button"}

    errors = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if isinstance(node.returns, ast.Name) and node.returns.id in forward_ref_names:
                errors.append(f"{node.name}() return: bare {node.returns.id}")
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                if isinstance(arg.annotation, ast.Name) and arg.annotation.id in forward_ref_names:
                    errors.append(f"{node.name}({arg.arg}): bare {arg.annotation.id}")

    assert not errors, (
        "Found bare forward-reference annotations that would cause NameError:\n"
        + "\n".join(f"  - {e}" for e in errors)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_utils_compiles_cleanly():
    """gradio/utils.py compiles without syntax errors after annotation changes."""
    module_code = compile(open(UTILS).read(), UTILS, "exec")
    assert module_code is not None


# [static] pass_to_pass
def test_not_stub():
    """utils.py retains full implementation (watchfn, BaseReloader, safe_join present)."""
    src = open(UTILS).read()
    assert "def watchfn" in src, "watchfn function missing"
    assert "class BaseReloader" in src, "BaseReloader class missing"
    assert "def safe_join" in src, "safe_join function missing"
    assert len(src.splitlines()) > 400, "File suspiciously short — likely stubbed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD tests from the repo that should pass
# on both base commit and after the fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_reload_tests():
    """Repo's reload tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", ".", "-e", "client/python", "-q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install gradio: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_reload.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Reload tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_type_hints_tests():
    """Repo's type hints tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", ".", "-e", "client/python", "hypothesis", "-q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install gradio: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::TestGetTypeHints", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Type hints tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_imports_cleanly():
    """Repo's main module imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-e", ".", "-e", "client/python", "-q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install gradio: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-c", "import gradio; print('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
        env={**os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Failed to import gradio: {r.stderr[-500:]}"
    assert "OK" in r.stdout, "Import test did not complete successfully"
