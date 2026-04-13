"""
Task: vllm-cuda-event-reuse-race
Repo: vllm @ b2b2c5239ec65fc6ba1109b0d06cb7462d99b70e
PR:   39115

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
ASYNC_UTILS = f"{REPO}/vllm/v1/worker/gpu/async_utils.py"
MODEL_RUNNER = f"{REPO}/vllm/v1/worker/gpu/model_runner.py"


def _get_required_init_params(tree: ast.Module, class_name: str) -> list[str]:
    """Return REQUIRED (no default) parameter names of __init__ for the given class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    args = item.args
                    num_defaults = len(args.defaults)
                    num_args = len(args.args)
                    num_required = num_args - num_defaults
                    required = [a.arg for a in args.args[:num_required]]
                    return [p for p in required if p != "self"]
    raise AssertionError(f"Class {class_name}.__init__ not found")


def _init_body_has_event_creation(tree: ast.Module, class_name: str) -> bool:
    """Check if __init__ of class_name contains a torch.cuda.Event() call."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    return _body_creates_cuda_event(item)
    return False


def _body_creates_cuda_event(func_node: ast.FunctionDef) -> bool:
    """Check if the function body contains torch.cuda.Event() creation."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            call_str = ast.dump(node.func)
            if "Event" in call_str and "cuda" in call_str:
                return True
    return False


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    r = subprocess.run(
        ["ruff", "check", ASYNC_UTILS, MODEL_RUNNER],
        capture_output=True, text=True, timeout=600, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    r = subprocess.run(
        ["ruff", "format", "--check", ASYNC_UTILS, MODEL_RUNNER],
        capture_output=True, text=True, timeout=600, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_mypy_check():
    """Repo's mypy typecheck passes on modified files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "mypy", "pydantic", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    r = subprocess.run(
        ["mypy", "--ignore-missing-imports", ASYNC_UTILS, MODEL_RUNNER],
        capture_output=True, text=True, timeout=600, cwd=REPO
    )
    assert r.returncode == 0, f"mypy check failed: {r.stdout} {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_typos_check():
    """Repo's typos spell check passes on modified files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "typos", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    r = subprocess.run(
        ["typos", ASYNC_UTILS, MODEL_RUNNER],
        capture_output=True, text=True, timeout=600, cwd=REPO
    )
    assert r.returncode == 0, f"typos check failed: {r.stdout} {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_spdx_headers():
    """Repo's SPDX license header check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_spdx_header.py",
         ASYNC_UTILS, MODEL_RUNNER],
        capture_output=True, text=True, timeout=600, cwd=REPO
    )
    assert r.returncode == 0, f"SPDX header check failed: {r.stdout} {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_forbidden_imports():
    """Repo's forbidden imports check passes on modified files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "regex", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_forbidden_imports.py",
         ASYNC_UTILS, MODEL_RUNNER],
        capture_output=True, text=True, timeout=600, cwd=REPO
    )
    assert r.returncode == 0, f"Forbidden imports check failed: {r.stdout} {r.stderr}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(ASYNC_UTILS, doraise=True)
    py_compile.compile(MODEL_RUNNER, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_async_output_no_shared_event_param():
    """AsyncOutput.__init__ must not accept a required copy_event parameter."""
    src = Path(ASYNC_UTILS).read_text()
    tree = ast.parse(src)
    required = _get_required_init_params(tree, "AsyncOutput")
    assert "copy_event" not in required, (
        "AsyncOutput.__init__ still requires copy_event as a parameter"
    )


# [pr_diff] fail_to_pass
def test_async_pooling_no_shared_event_param():
    """AsyncPoolingOutput.__init__ must not accept a required copy_event parameter."""
    src = Path(ASYNC_UTILS).read_text()
    tree = ast.parse(src)
    required = _get_required_init_params(tree, "AsyncPoolingOutput")
    assert "copy_event" not in required, (
        "AsyncPoolingOutput.__init__ still requires copy_event as a parameter"
    )


# [pr_diff] fail_to_pass
def test_async_output_creates_own_event():
    """AsyncOutput.__init__ must create its own torch.cuda.Event() internally."""
    src = Path(ASYNC_UTILS).read_text()
    tree = ast.parse(src)
    assert _init_body_has_event_creation(tree, "AsyncOutput"), (
        "AsyncOutput.__init__ does not create a torch.cuda.Event()"
    )


# [pr_diff] fail_to_pass
def test_async_pooling_creates_own_event():
    """AsyncPoolingOutput.__init__ must create its own torch.cuda.Event() internally."""
    src = Path(ASYNC_UTILS).read_text()
    tree = ast.parse(src)
    assert _init_body_has_event_creation(tree, "AsyncPoolingOutput"), (
        "AsyncPoolingOutput.__init__ does not create a torch.cuda.Event()"
    )


# [pr_diff] fail_to_pass
def test_model_runner_no_shared_event():
    """GPUModelRunner must not store a shared output_copy_event attribute."""
    src = Path(MODEL_RUNNER).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GPUModelRunner":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if (isinstance(target, ast.Attribute)
                                        and isinstance(target.value, ast.Name)
                                        and target.value.id == "self"
                                        and target.attr == "output_copy_event"):
                                    raise AssertionError(
                                        "GPUModelRunner.__init__ still creates "
                                        "self.output_copy_event"
                                    )
                    return
    raise AssertionError("GPUModelRunner.__init__ not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_async_output_init_not_stub():
    """AsyncOutput.__init__ has real logic (not just pass/return)."""
    src = Path(ASYNC_UTILS).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AsyncOutput":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    real_stmts = [
                        s for s in item.body
                        if not isinstance(s, ast.Pass)
                        and not (isinstance(s, ast.Expr) and isinstance(s.value, (ast.Constant, ast.Str)))
                    ]
                    assert len(real_stmts) >= 5, (
                        f"AsyncOutput.__init__ has only {len(real_stmts)} statements"
                    )
                    return
    raise AssertionError("AsyncOutput.__init__ not found")
