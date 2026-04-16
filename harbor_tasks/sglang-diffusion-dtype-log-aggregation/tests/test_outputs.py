"""
Task: sglang-diffusion-dtype-log-aggregation
Repo: sgl-project/sglang @ 7160b6cb76d3619468b219ea066fcb6358a8000e

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path
from collections import Counter, defaultdict

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/multimodal_gen/runtime/loader/fsdp_load.py"


def _read_source():
    return Path(TARGET).read_text()


def _parse_tree(source=None):
    if source is None:
        source = _read_source()
    return ast.parse(source), source


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


def _discover_summary_formatter():
    """Discover the summary formatter function by behavior (accepts Counter/defaultdict, returns string)."""
    import textwrap
    import types

    source = _read_source()
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        func_src = "from __future__ import annotations\n" + textwrap.dedent(
            "".join(lines[node.lineno - 1 : node.end_lineno])
        )

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
            fn = env[node.name]

            # Test if this function behaves like a summary formatter
            test_counts = Counter()
            test_examples = defaultdict(list)
            test_counts[("torch.float32", "torch.bfloat16")] = 50
            test_examples[("torch.float32", "torch.bfloat16")] = ["blocks.0.weight"]

            result = fn(test_counts, test_examples)

            # Check it returns a non-empty string with expected content
            if isinstance(result, str) and len(result) > 0:
                if "50" in result and "float32" in result:
                    return fn, node.name
        except Exception:
            continue

    return None, None


def _run_formatter_with_inputs(counts, examples):
    """Run the discovered formatter function with given inputs via subprocess."""
    formatter_fn, formatter_name = _discover_summary_formatter()
    assert formatter_fn is not None, "No summary formatter function found"

    import textwrap
    import types

    source = _read_source()
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == formatter_name:
            func_src = "from __future__ import annotations\n" + textwrap.dedent(
                "".join(lines[node.lineno - 1 : node.end_lineno])
            )

            mock_torch = types.ModuleType("torch")
            mock_torch.dtype = type("dtype", (), {})

            env = {
                "Counter": Counter,
                "defaultdict": defaultdict,
                "torch": mock_torch,
                "__builtins__": __builtins__,
            }

            exec(func_src, env)
            fn = env[formatter_name]
            return fn(counts, examples)

    raise RuntimeError("Formatter function disappeared during test")


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
    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.float32", "torch.bfloat16")] = 50
    examples[("torch.float32", "torch.bfloat16")] = ["blocks.0.weight", "blocks.1.bias", "embed.pos"]
    counts[("torch.float16", "torch.bfloat16")] = 12
    examples[("torch.float16", "torch.bfloat16")] = ["norm.weight"]

    result = _run_formatter_with_inputs(counts, examples)

    assert isinstance(result, str) and len(result) > 0
    assert "50" in result, f"Missing count 50 in: {result}"
    assert "12" in result, f"Missing count 12 in: {result}"
    assert "float32" in result, f"Missing float32 in: {result}"
    assert "float16" in result, f"Missing float16 in: {result}"
    assert "bfloat16" in result, f"Missing bfloat16 in: {result}"
    assert any(name in result for name in ["blocks.0.weight", "blocks.1.bias", "embed.pos"]), f"Missing example names in: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_empty_examples():
    """Summary function handles pairs with no example parameter names."""
    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.float32", "torch.bfloat16")] = 7
    examples[("torch.float32", "torch.bfloat16")] = []

    result = _run_formatter_with_inputs(counts, examples)

    assert isinstance(result, str)
    assert "7" in result, f"Missing count with empty examples: {result}"
    assert "float32" in result, f"Missing dtype in: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_single_pair():
    """Summary function works correctly with a single mismatch type."""
    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.int8", "torch.float32")] = 100
    examples[("torch.int8", "torch.float32")] = ["fc.weight", "fc.bias"]

    result = _run_formatter_with_inputs(counts, examples)

    assert "int8" in result, f"Missing int8 in: {result}"
    assert "100" in result, f"Missing count 100 in: {result}"
    assert "fc.weight" in result or "fc.bias" in result, f"Missing example in: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_no_raw_repr():
    """Summary output is human-readable, not raw Counter/defaultdict repr."""
    counts = Counter()
    examples = defaultdict(list)
    counts[("torch.float32", "torch.bfloat16")] = 5
    examples[("torch.float32", "torch.bfloat16")] = ["layer.0.w"]

    result = _run_formatter_with_inputs(counts, examples)

    assert "Counter(" not in result, f"Raw Counter repr in output: {result}"
    assert "defaultdict(" not in result, f"Raw defaultdict repr in output: {result}"


# [pr_diff] fail_to_pass
def test_summary_formatter_function_exists():
    """A module-level function exists that can format dtype mismatch summaries."""
    formatter_fn, formatter_name = _discover_summary_formatter()
    assert formatter_fn is not None, "No summary formatter function found at module level"
    assert formatter_name is not None


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
def test_repo_ruff():
    """Repo's ruff lint (F401, F821) passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black():
    """Repo's black formatting check passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr[-500:]}"

    r = subprocess.run(
        ["black", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Repo's codespell check passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "codespell", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install codespell: {r.stderr[-500:]}"

    r = subprocess.run(
        ["codespell", "--config", f"{REPO}/.codespellrc", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo's isort import ordering check passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr[-500:]}"

    r = subprocess.run(
        ["isort", "--check-only", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_ast():
    """Repo's pre-commit check-ast hook passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pre-commit", "run", "check-ast", "--files", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit check-ast failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_debug_statements():
    """Repo's pre-commit debug-statements hook passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pre-commit", "run", "debug-statements", "--files", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit debug-statements failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_trailing_whitespace():
    """Repo's pre-commit trailing-whitespace hook passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--files", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit trailing-whitespace failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_eof_fixer():
    """Repo's pre-commit end-of-file-fixer hook passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--files", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit end-of-file-fixer failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_merge_conflict():
    """Repo's pre-commit check-merge-conflict hook passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pre-commit", "run", "check-merge-conflict", "--files", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit check-merge-conflict failed:\n{r.stderr[-500:]}"


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
