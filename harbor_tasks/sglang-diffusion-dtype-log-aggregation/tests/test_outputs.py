"""
Task: sglang-diffusion-dtype-log-aggregation
Repo: sgl-project/sglang @ 7160b6cb76d3619468b219ea066fcb6358a8000e
PR:   #21552

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
import types
from collections import Counter, defaultdict
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/multimodal_gen/runtime/loader/fsdp_load.py"


def _read_source():
    return Path(TARGET).read_text()


def _parse_tree(source=None):
    if source is None:
        source = _read_source()
    return ast.parse(source), source


def _find_summary_formatter():
    """Find the dtype mismatch summary/format function by behavior, not exact name.

    Searches module-level functions for one that accepts (Counter, defaultdict)
    and returns a human-readable string. This avoids hard-coding the gold-patch
    function name so alternative implementations also pass.
    """
    tree, source = _parse_tree()
    lines = source.splitlines(keepends=True)

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        # Skip known pre-existing functions
        if node.name in (
            "_make_param_like",
            "load_model_from_full_model_state_dict",
            "shard_model",
        ):
            continue

        func_src = "from __future__ import annotations\n" + textwrap.dedent(
            "".join(lines[node.lineno - 1 : node.end_lineno])
        )
        # Provide a mock torch module so type annotations like torch.dtype don't fail
        mock_torch = types.ModuleType("torch")
        mock_torch.dtype = type("dtype", (), {})
        env = {
            "Counter": Counter,
            "defaultdict": defaultdict,
            "torch": mock_torch,
            "__builtins__": __builtins__,
        }
        try:
            exec(func_src, env)
            func = env[node.name]
            counts = Counter()
            examples = defaultdict(list)
            counts[("torch.float32", "torch.bfloat16")] = 3
            examples[("torch.float32", "torch.bfloat16")] = ["w0"]
            result = func(counts, examples)
            if isinstance(result, str) and len(result) > 0:
                return func
        except Exception:
            continue
    return None


def _find_loading_func_and_loop():
    """Return (func_node, for_loop_node, tree) for load_model_from_full_model_state_dict."""
    tree, _ = _parse_tree()
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "load_model_from_full_model_state_dict":
            func = node
            break
    assert func is not None, "load_model_from_full_model_state_dict not found"

    for_loop = None
    for node in ast.walk(func):
        if isinstance(node, ast.For):
            iter_src = ast.dump(node.iter)
            if "sorted" in iter_src or "param_name" in iter_src.lower():
                for_loop = node
                break
    assert for_loop is not None, "Main parameter loading loop not found"
    return func, for_loop, tree


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax():
    """Target file must parse without syntax errors."""
    source = _read_source()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_summary_formatter_multiple_types():
    """Summary function aggregates multiple dtype mismatch pairs with counts and examples."""
    fmt = _find_summary_formatter()
    assert fmt is not None, "No summary formatter function found at module level"

    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.float32", "torch.bfloat16")] = 50
    examples[("torch.float32", "torch.bfloat16")] = [
        "blocks.0.weight",
        "blocks.1.bias",
        "embed.pos",
    ]
    counts[("torch.float16", "torch.bfloat16")] = 12
    examples[("torch.float16", "torch.bfloat16")] = ["norm.weight"]

    result = fmt(counts, examples)
    assert isinstance(result, str) and len(result) > 0
    # Both dtype pairs must be represented
    assert "float32" in result, f"Missing float32 in: {result}"
    assert "float16" in result, f"Missing float16 in: {result}"
    assert "bfloat16" in result, f"Missing bfloat16 in: {result}"
    # Counts must appear
    assert "50" in result, f"Missing count 50 in: {result}"
    assert "12" in result, f"Missing count 12 in: {result}"
    # At least one example name must appear
    assert any(
        name in result for name in ["blocks.0.weight", "blocks.1.bias", "embed.pos"]
    ), f"Missing example names in: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_empty_examples():
    """Summary function handles pairs with no example parameter names."""
    fmt = _find_summary_formatter()
    assert fmt is not None, "No summary formatter function found"

    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.float32", "torch.bfloat16")] = 7
    examples[("torch.float32", "torch.bfloat16")] = []  # no examples

    result = fmt(counts, examples)
    assert isinstance(result, str)
    assert "7" in result, f"Missing count with empty examples: {result}"
    assert "float32" in result, f"Missing dtype in: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_single_pair():
    """Summary function works correctly with a single mismatch type."""
    fmt = _find_summary_formatter()
    assert fmt is not None, "No summary formatter function found"

    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.int8", "torch.float32")] = 100
    examples[("torch.int8", "torch.float32")] = ["fc.weight", "fc.bias"]

    result = fmt(counts, examples)
    assert "int8" in result, f"Missing int8 in: {result}"
    assert "100" in result, f"Missing count 100 in: {result}"
    assert "fc.weight" in result or "fc.bias" in result, f"Missing example in: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_no_raw_repr():
    """Summary output is human-readable, not raw Counter/defaultdict repr."""
    fmt = _find_summary_formatter()
    assert fmt is not None, "No summary formatter function found"

    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.float32", "torch.bfloat16")] = 5
    examples[("torch.float32", "torch.bfloat16")] = ["layer.0.w"]

    result = fmt(counts, examples)
    assert "Counter(" not in result, f"Raw Counter repr in output: {result}"
    assert "defaultdict(" not in result, f"Raw defaultdict repr in output: {result}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural (AST-based, torch not available)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
# AST-only because: torch/CUDA deps not installed — cannot import or run loader
def test_no_per_param_warnings_in_loop():
    """Loading loop must not emit per-parameter logger.warning for dtype mismatches."""
    _, for_loop, _ = _find_loading_func_and_loop()

    for node in ast.walk(for_loop):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if not (
            node.func.attr == "warning"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
        ):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                assert "Dtype mismatch for" not in arg.value, (
                    "Per-parameter 'Dtype mismatch for' warning still in loop"
                )


# [pr_diff] fail_to_pass
# AST-only because: torch/CUDA deps not installed — cannot import or run loader
def test_quantized_dtypes_not_redefined_in_loop():
    """Quantized dtype tuple/set must not be re-created inside the loading loop."""
    func, _, _ = _find_loading_func_and_loop()

    for node in ast.walk(func):
        if not isinstance(node, ast.For):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Assign):
                for target in inner.targets:
                    if isinstance(target, ast.Name) and "quantiz" in target.id.lower():
                        assert False, (
                            f"{target.id} re-defined inside loop — should be at broader scope"
                        )


# [pr_diff] fail_to_pass
# AST-only because: torch/CUDA deps not installed — cannot import or run loader
def test_aggregated_summary_after_loop():
    """Aggregated dtype summary log must exist after the main loading loop."""
    func, for_loop, _ = _find_loading_func_and_loop()
    loop_end = for_loop.end_lineno

    found = False
    for node in ast.walk(func):
        if not hasattr(node, "lineno") or node.lineno <= loop_end:
            continue
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if not (
            node.func.attr in ("debug", "warning", "info")
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
        ):
            continue
        call_dump = ast.dump(node).lower()
        if any(kw in call_dump for kw in ["dtype", "mismatch", "cast", "summary"]):
            found = True
            break

    assert found, "No aggregated dtype summary log found after loading loop"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_function_signatures_preserved():
    """Core function signatures must remain unchanged."""
    tree, _ = _parse_tree()

    required = {
        "load_model_from_full_model_state_dict": [
            "model",
            "full_sd_iterator",
            "device",
            "param_dtype",
        ],
        "_make_param_like": ["actual_param", "tensor"],
        "shard_model": ["model"],
    }

    for func_name, required_args in required.items():
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                found = True
                arg_names = [a.arg for a in node.args.args]
                for req in required_args:
                    assert req in arg_names, f"{func_name} missing required arg '{req}'"
                break
        assert found, f"Function {func_name} not found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from repo skill files
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-add-model/SKILL.md:333-335 @ 7160b6cb76d3619468b219ea066fcb6358a8000e
# AST-only because: torch/CUDA deps not installed — cannot import module
def test_logger_uses_init_logger():
    """Logger must be initialized via init_logger(__name__) from logging_utils."""
    source = _read_source()
    tree = ast.parse(source)

    # Check import of init_logger
    has_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "logging_utils" in node.module:
                imported_names = [alias.name for alias in node.names]
                if "init_logger" in imported_names:
                    has_import = True
                    break
    assert has_import, "Must import init_logger from logging_utils"

    # Check logger = init_logger(__name__)
    has_init = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "logger":
                    if (
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Name)
                        and node.value.func.id == "init_logger"
                    ):
                        has_init = True
                        break
    assert has_init, "logger must be initialized with init_logger(__name__)"
