"""
Task: vllm-qwen3-dual-stream-compile-regression
Repo: vllm-project/vllm @ 74056039b776776ed29eb0649e51ac6780592a4c
PR:   #38152

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

# AST-only because: vllm model files import torch, triton, CUDA kernels —
# cannot be imported or executed in a CPU-only test container.

REPO = "/workspace/vllm"
QWEN3_NEXT = f"{REPO}/vllm/model_executor/models/qwen3_next.py"
QWEN3_5 = f"{REPO}/vllm/model_executor/models/qwen3_5.py"


def _parse_file(filepath: str) -> tuple[str, ast.Module]:
    """Read and parse a Python file, returning (source, tree)."""
    source = Path(filepath).read_text()
    return source, ast.parse(source)


def _get_class_method(tree: ast.Module, class_substr: str, method_name: str) -> ast.FunctionDef:
    """Find a method AST node from a class matching class_substr."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and class_substr in node.name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return item
    raise AssertionError(f"Could not find {class_substr}.{method_name}")


def _get_method_source(filepath: str, class_substr: str, method_name: str) -> str:
    """Extract the source text of a method from a class matching class_substr."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    method = _get_class_method(tree, class_substr, method_name)
    seg = ast.get_source_segment(source, method)
    if seg:
        return seg
    lines = source.splitlines()
    return "\n".join(lines[method.lineno - 1 : method.end_lineno])


def _calls_in_method(tree: ast.Module, class_substr: str, method_name: str) -> list[str]:
    """Return dotted call names (e.g. 'self.in_proj_qkvz') in a method."""
    method = _get_class_method(tree, class_substr, method_name)
    names = []
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            func = node.func
            parts = []
            while isinstance(func, ast.Attribute):
                parts.append(func.attr)
                func = func.value
            if isinstance(func, ast.Name):
                parts.append(func.id)
            parts.reverse()
            names.append(".".join(parts))
    return names


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both model files must be valid Python."""
    for path in (QWEN3_NEXT, QWEN3_5):
        source = Path(path).read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {path}: {e}") from e


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core bug fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_qwen3next_forward_no_custom_op():
    """qwen3_next GatedDeltaNet.forward must not call gdn_in_proj custom op."""
    _, tree = _parse_file(QWEN3_NEXT)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    gdn_calls = [c for c in calls if "gdn_in_proj" in c]
    assert not gdn_calls, (
        f"forward still routes through gdn_in_proj custom op: {gdn_calls}"
    )


# [pr_diff] fail_to_pass
def test_qwen35_forward_no_custom_op():
    """qwen3_5 GatedDeltaNet.forward must not call gdn_in_proj custom op."""
    _, tree = _parse_file(QWEN3_5)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    gdn_calls = [c for c in calls if "gdn_in_proj" in c]
    assert not gdn_calls, (
        f"forward still routes through gdn_in_proj custom op: {gdn_calls}"
    )


# [pr_diff] fail_to_pass
def test_gdn_in_proj_not_registered():
    """gdn_in_proj must not be registered as a custom op at module level."""
    _, tree = _parse_file(QWEN3_NEXT)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            # Check keyword arg: op_name="gdn_in_proj"
            for kw in call.keywords:
                if (
                    kw.arg == "op_name"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value == "gdn_in_proj"
                ):
                    raise AssertionError(
                        "gdn_in_proj is still registered as a custom op"
                    )
            # Check positional arg: "gdn_in_proj"
            if (
                call.args
                and isinstance(call.args[0], ast.Constant)
                and call.args[0].value == "gdn_in_proj"
            ):
                raise AssertionError(
                    "gdn_in_proj is still registered as a custom op"
                )


# [pr_diff] fail_to_pass
def test_no_dual_stream_infra():
    """__init__ must not set up aux_stream or cuda Events for dual-stream."""
    _, tree = _parse_file(QWEN3_NEXT)
    init = _get_class_method(tree, "GatedDeltaNet", "__init__")
    found = []
    for node in ast.walk(init):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and t.attr in (
                    "aux_stream",
                    "events",
                ):
                    found.append(t.attr)
    assert not found, f"__init__ still sets up dual-stream infra: {', '.join(found)}"


# [pr_diff] fail_to_pass
def test_dead_code_removed():
    """gdn_in_proj, gdn_in_proj_fake, and _forward_in_proj must be removed."""
    _, tree = _parse_file(QWEN3_NEXT)

    # Check module-level dead functions
    dead_module = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name in (
            "gdn_in_proj",
            "gdn_in_proj_fake",
        ):
            dead_module.append(node.name)

    # Check class-level dead method
    dead_class = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "GatedDeltaNet" in node.name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "_forward_in_proj":
                    dead_class.append("_forward_in_proj")

    dead = dead_module + dead_class
    assert not dead, f"Dead code still present: {', '.join(dead)}"


# [pr_diff] fail_to_pass
def test_unused_imports_removed():
    """Imports only needed for dual-stream (maybe_execute_in_parallel, aux_stream) must be removed."""
    _, tree = _parse_file(QWEN3_NEXT)

    dead_imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.name
                if name in ("maybe_execute_in_parallel", "aux_stream"):
                    dead_imports.append(name)

    assert not dead_imports, (
        f"Unused dual-stream imports still present: {', '.join(dead_imports)}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression / anti-over-deletion
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_qwen3next_direct_projection():
    """qwen3_next forward must call in_proj_qkvz and in_proj_ba directly."""
    _, tree = _parse_file(QWEN3_NEXT)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    called_attrs = set()
    for c in calls:
        parts = c.split(".")
        if len(parts) >= 2:
            called_attrs.add(parts[-1])
    missing = {"in_proj_qkvz", "in_proj_ba"} - called_attrs
    assert not missing, f"forward missing direct calls to: {', '.join(missing)}"


# [pr_diff] pass_to_pass
def test_qwen35_direct_projection():
    """qwen3_5 forward must call in_proj_qkvz and in_proj_ba directly."""
    _, tree = _parse_file(QWEN3_5)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    called_attrs = set()
    for c in calls:
        parts = c.split(".")
        if len(parts) >= 2:
            called_attrs.add(parts[-1])
    missing = {"in_proj_qkvz", "in_proj_ba"} - called_attrs
    assert not missing, f"forward missing direct calls to: {', '.join(missing)}"


# [pr_diff] pass_to_pass
def test_attention_core_op_preserved():
    """gdn_attention_core custom op must still be registered (not over-deleted)."""
    _, tree = _parse_file(QWEN3_NEXT)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            for kw in call.keywords:
                if (
                    kw.arg == "op_name"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value == "gdn_attention_core"
                ):
                    return
            if (
                call.args
                and isinstance(call.args[0], ast.Constant)
                and call.args[0].value == "gdn_attention_core"
            ):
                return
    raise AssertionError(
        "gdn_attention_core custom op registration is missing (over-deletion)"
    )


# [static] pass_to_pass
def test_forward_not_stub():
    """GatedDeltaNet.forward must have real logic (anti-stub guard)."""
    for filepath in (QWEN3_NEXT, QWEN3_5):
        _, tree = _parse_file(filepath)
        method = _get_class_method(tree, "GatedDeltaNet", "forward")
        # A real forward method has many statements; a stub has <=2
        stmts = [s for s in ast.walk(method) if isinstance(s, ast.Assign)]
        assert len(stmts) >= 3, (
            f"GatedDeltaNet.forward in {filepath} appears to be a stub "
            f"(only {len(stmts)} assignments)"
        )
