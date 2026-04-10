"""
Task: vllm-model-loader-device-context
Repo: vllm-project/vllm @ af89140efc06c462ae531999b9f2db6ba0c7a528
PR:   #38426

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/model_executor/model_loader/base_loader.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_target():
    """Parse the target file and return (source, tree)."""
    src = Path(TARGET).read_text()
    return src, ast.parse(src)


def _find_load_model(tree):
    """Find the load_model FunctionDef node in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "load_model":
            return node
    return None


def _find_calls_under_device_with(node, in_device_ctx=False):
    """Walk AST tracking whether we're inside a With that uses target_device/torch.device."""
    results = {}
    if isinstance(node, ast.With):
        has_device = any(
            ("target_device" in ast.dump(item.context_expr)
             or "device" in ast.dump(item.context_expr).lower())
            and "set_default_torch_dtype" not in ast.dump(item.context_expr)
            for item in node.items
        )
        for child in ast.iter_child_nodes(node):
            results.update(_find_calls_under_device_with(child, in_device_ctx or has_device))
    elif isinstance(node, (ast.Expr, ast.Assign)):
        call_node = None
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call_node = node.value
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call_node = node.value

        if call_node is not None:
            func = call_node.func
            fname = ""
            if isinstance(func, ast.Name):
                fname = func.id
            elif isinstance(func, ast.Attribute):
                fname = func.attr
            if fname in ("log_model_inspection", "initialize_model"):
                results[fname] = in_device_ctx

        for child in ast.iter_child_nodes(node):
            results.update(_find_calls_under_device_with(child, in_device_ctx))
    else:
        for child in ast.iter_child_nodes(node):
            results.update(_find_calls_under_device_with(child, in_device_ctx))
    return results


def _find_calls_under_dtype_with(node, in_dtype_ctx=False):
    """Walk AST tracking whether we're inside a With that uses set_default_torch_dtype."""
    results = {}
    if isinstance(node, ast.With):
        has_dtype = any(
            "set_default_torch_dtype" in ast.dump(item.context_expr)
            for item in node.items
        )
        for child in ast.iter_child_nodes(node):
            results.update(_find_calls_under_dtype_with(child, in_dtype_ctx or has_dtype))
    elif isinstance(node, (ast.Expr, ast.Assign)):
        call_node = None
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call_node = node.value
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call_node = node.value

        if call_node is not None:
            func = call_node.func
            fname = ""
            if isinstance(func, ast.Name):
                fname = func.id
            elif isinstance(func, ast.Attribute):
                fname = func.attr
            if fname in ("log_model_inspection", "initialize_model"):
                results[fname] = in_dtype_ctx

        for child in ast.iter_child_nodes(node):
            results.update(_find_calls_under_dtype_with(child, in_dtype_ctx))
    else:
        for child in ast.iter_child_nodes(node):
            results.update(_find_calls_under_dtype_with(child, in_dtype_ctx))
    return results


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """base_loader.py must parse without syntax errors."""
    src = Path(TARGET).read_text()
    compile(src, TARGET, "exec")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands that work without GPU/network
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — ruff lint check
def test_repo_ruff_check():
    """Repo's ruff linter passes on base_loader.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff format check
def test_repo_ruff_format():
    """Repo's ruff format check passes on base_loader.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — typos spell check
def test_repo_typos():
    """Repo's typos spell checker passes on base_loader.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "typos", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["typos", TARGET],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: load_model requires full vllm + torch + GPU stack; the bug IS context manager nesting scope
def test_log_inspection_outside_device_context():
    """log_model_inspection must NOT run inside the target_device context manager.

    The bug: a combined `with dtype, device:` block causes log_model_inspection
    to execute under the device context, leading to GPU memory CI failures.
    The fix splits the contexts so log_model_inspection is outside device scope.
    """
    src, tree = _parse_target()
    load_model = _find_load_model(tree)
    assert load_model is not None, "load_model method not found"

    call_contexts = _find_calls_under_device_with(load_model)
    assert "log_model_inspection" in call_contexts, "log_model_inspection call not found in load_model"
    assert not call_contexts["log_model_inspection"], (
        "log_model_inspection runs inside the device context — "
        "it must be outside to avoid GPU memory side effects"
    )


# [pr_diff] fail_to_pass
# AST-only because: load_model requires full vllm + torch + GPU stack; the bug IS context manager nesting scope
def test_device_context_narrower_than_dtype():
    """The device context must be a strict subset of the dtype context.

    On the buggy base, both contexts share the same scope (combined `with`).
    The fix nests device inside dtype, so some operations (like log_model_inspection)
    run in dtype scope but outside device scope — proving the device context is narrower.
    """
    src, tree = _parse_target()
    load_model = _find_load_model(tree)
    assert load_model is not None, "load_model method not found"

    device_ctx = _find_calls_under_device_with(load_model)
    dtype_ctx = _find_calls_under_dtype_with(load_model)

    # At least one function must be inside dtype but outside device
    has_dtype_only = False
    for fname in ("log_model_inspection", "initialize_model"):
        if fname in device_ctx and fname in dtype_ctx:
            if dtype_ctx[fname] and not device_ctx[fname]:
                has_dtype_only = True

    assert has_dtype_only, (
        "No function found that is inside dtype context but outside device context — "
        "the device context must be narrower than dtype (nested, not combined)"
    )


# [pr_diff] pass_to_pass
# AST-only because: load_model requires full vllm + torch + GPU stack; the bug IS context manager nesting scope
def test_initialize_model_inside_device_context():
    """initialize_model must still run INSIDE the target_device context.

    The fix separates the context managers but must preserve the device context
    around model initialization — only log_model_inspection moves out.
    """
    src, tree = _parse_target()
    load_model = _find_load_model(tree)
    assert load_model is not None, "load_model method not found"

    call_contexts = _find_calls_under_device_with(load_model)
    assert "initialize_model" in call_contexts, "initialize_model call not found in load_model"
    assert call_contexts["initialize_model"], (
        "initialize_model is NOT inside a device context — "
        "model init still requires the target device scope"
    )


# [pr_diff] pass_to_pass
# AST-only because: load_model requires full vllm + torch + GPU stack; the bug IS context manager nesting scope
def test_log_inspection_inside_dtype_context():
    """log_model_inspection must still run inside the set_default_torch_dtype context.

    The fix moves log_model_inspection out of the device context but it must remain
    within the dtype context. An overly aggressive fix that removes both contexts
    would break dtype handling.
    """
    src, tree = _parse_target()
    load_model = _find_load_model(tree)
    assert load_model is not None, "load_model method not found"

    call_contexts = _find_calls_under_dtype_with(load_model)
    assert "log_model_inspection" in call_contexts, "log_model_inspection call not found in load_model"
    assert call_contexts["log_model_inspection"], (
        "log_model_inspection is NOT inside the dtype context — "
        "it must remain within set_default_torch_dtype scope"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
# AST-only because: load_model requires full vllm + torch + GPU stack; checking class/method presence
def test_key_structure_preserved():
    """BaseModelLoader class and its key methods/calls must be preserved."""
    src, tree = _parse_target()

    class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    assert "BaseModelLoader" in class_names, "BaseModelLoader class missing"

    # Check methods inside BaseModelLoader
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BaseModelLoader":
            method_names = {
                n.name for n in ast.walk(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            assert "load_model" in method_names, "load_model method missing"
            assert "load_weights" in method_names, "load_weights method missing"
            break

    # Check key calls in load_model body
    load_model = _find_load_model(tree)
    func_src = "\n".join(src.splitlines()[load_model.lineno - 1:load_model.end_lineno])
    for name in ["initialize_model", "log_model_inspection", "load_weights", "process_weights_after_loading"]:
        assert name in func_src, f"load_model missing call to {name}"


# [static] pass_to_pass
# AST-only because: load_model requires full vllm + torch + GPU stack; anti-stub structural check
def test_not_stub():
    """base_loader.py must have real content — not a gutted stub."""
    src, tree = _parse_target()
    lines = src.splitlines()
    assert len(lines) >= 60, f"Only {len(lines)} lines (expected 60+)"

    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    assert len(funcs) >= 3, f"Only {len(funcs)} functions (expected 3+)"

    load_model = _find_load_model(tree)
    assert load_model is not None, "load_model not found"
    stmts = [s for s in ast.walk(load_model)
             if isinstance(s, (ast.Assign, ast.Expr, ast.Return, ast.With, ast.If, ast.For))]
    assert len(stmts) >= 5, f"load_model has only {len(stmts)} statements — looks like a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:42 @ af89140efc06c462ae531999b9f2db6ba0c7a528
def test_no_bare_pip_install():
    """Changed files must not introduce bare `pip install` (must use uv)."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    changed_files = [f for f in r.stdout.strip().splitlines() if f]

    for cf in changed_files:
        fpath = Path(REPO) / cf
        if not fpath.is_file():
            continue
        content = fpath.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.split("#")[0]  # ignore comments
            if "pip install" in stripped and "uv pip" not in stripped and "uv " not in stripped:
                raise AssertionError(
                    f"{cf}:{i} contains bare 'pip install' — "
                    f"AGENTS.md requires all pip commands go through uv"
                )
