"""
Task: prime-rl-ckpt-cpu-offload-oom
Repo: prime-rl @ 04da032d968418edef069173d368e3a6080bfcb2
PR:   PrimeIntellect-ai/prime-rl#2154

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This fix addresses CUDA GPU memory management (torch.cuda.empty_cache,
gc.collect for stale tensor references). Since tests run on CPU-only Docker,
we use AST analysis — the justified exception for GPU/CUDA-dependent code paths.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/prime-rl"
CKPT_FILE = Path(f"{REPO}/src/prime_rl/trainer/ckpt.py")


def _get_source():
    return CKPT_FILE.read_text()


def _find_method(tree, class_name, method_name):
    """Find a method node inside a class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return item
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """ckpt.py must parse without syntax errors."""
    source = _get_source()
    compile(source, str(CKPT_FILE), "exec")


# [repo_tests] pass_to_pass - Repo CI: ruff lint check
def test_repo_ruff_check():
    """Repo's ruff lint check passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", str(CKPT_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Repo CI: ruff format check
def test_repo_ruff_format():
    """Repo's ruff format check passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", str(CKPT_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gc_imported():
    """gc module must be imported — needed for gc.collect() to break circular refs."""
    source = _get_source()
    tree = ast.parse(source)
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])
    assert "gc" in imported_names, (
        "ckpt.py must import the gc module to call gc.collect() for memory cleanup"
    )


# [pr_diff] fail_to_pass
def test_memory_reclamation_on_cpu_offload():
    """load_state_dict must call gc.collect() AND torch.cuda.empty_cache()
    to reclaim GPU memory after loading with CPUOffloadOptimizer."""
    source = _get_source()
    tree = ast.parse(source)
    method = _find_method(tree, "AppState", "load_state_dict")
    assert method is not None, "AppState.load_state_dict not found"

    method_source = ast.get_source_segment(source, method)
    assert method_source is not None, "Could not extract load_state_dict source"

    # Must call gc.collect() to break circular references holding GPU tensors
    assert "gc.collect()" in method_source, (
        "load_state_dict must call gc.collect() to free circular GPU tensor references"
    )
    # Must call torch.cuda.empty_cache() to return freed GPU memory to CUDA allocator
    assert "empty_cache()" in method_source, (
        "load_state_dict must call torch.cuda.empty_cache() to reclaim GPU memory"
    )


# [pr_diff] fail_to_pass
def test_cleanup_gated_on_offload():
    """Memory cleanup must be conditional on CPUOffloadOptimizer presence,
    not unconditional — avoids unnecessary gc/cache flush overhead."""
    source = _get_source()
    tree = ast.parse(source)
    method = _find_method(tree, "AppState", "load_state_dict")
    assert method is not None, "AppState.load_state_dict not found"

    # Look for gc.collect or empty_cache inside an If block within the method
    found_conditional_cleanup = False
    for node in ast.walk(method):
        if isinstance(node, ast.If):
            if_source = ast.get_source_segment(source, node)
            if if_source and ("gc.collect" in if_source or "empty_cache" in if_source):
                found_conditional_cleanup = True
                break

    assert found_conditional_cleanup, (
        "Memory cleanup (gc.collect/empty_cache) must be inside a conditional block "
        "that checks for CPUOffloadOptimizer, not called unconditionally"
    )

    # The condition must relate to CPUOffloadOptimizer detection
    method_source = ast.get_source_segment(source, method)
    assert "CPUOffloadOptimizer" in method_source, (
        "load_state_dict must reference CPUOffloadOptimizer to detect CPU offload"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_load_state_dict_not_stub():
    """load_state_dict must have substantial logic (not a stub)."""
    source = _get_source()
    tree = ast.parse(source)
    method = _find_method(tree, "AppState", "load_state_dict")
    assert method is not None, "AppState.load_state_dict not found"

    # Count non-trivial statements (exclude pass, docstrings, bare expressions)
    stmts = [
        s for s in ast.walk(method)
        if isinstance(s, (ast.Assign, ast.AugAssign, ast.Call, ast.If, ast.For,
                          ast.Return, ast.With))
    ]
    assert len(stmts) >= 5, (
        f"load_state_dict has only {len(stmts)} substantive statements — "
        "expected at least 5 for a real implementation"
    )
