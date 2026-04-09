"""
Task: vllm-encoder-cudagraph-import-paths
Repo: vllm @ f53fa26e05c476a43f6db048a9e3b43bcb2b72fb
PR:   38997

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The encoder_cudagraph modules live at vllm/v1/worker/ but several files
import them via the non-existent path vllm.v1.worker.gpu.mm.  These are
GPU/CUDA-graph modules that cannot be imported on CPU, so we verify
import paths via AST parsing.
"""

import ast
import os
from pathlib import Path

REPO = "/workspace/vllm"

STALE_PREFIX = "vllm.v1.worker.gpu.mm.encoder_cudagraph"
CORRECT_DEFS = "vllm.v1.worker.encoder_cudagraph_defs"
CORRECT_MGR = "vllm.v1.worker.encoder_cudagraph"


def _collect_import_from_modules(source: str) -> list[str]:
    """Return all 'from X import ...' module strings in source."""
    tree = ast.parse(source)
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_encoder_cudagraph_internal_import():
    """encoder_cudagraph.py must import encoder_cudagraph_defs from
    vllm.v1.worker, not vllm.v1.worker.gpu.mm."""
    src = Path(f"{REPO}/vllm/v1/worker/encoder_cudagraph.py").read_text()
    modules = _collect_import_from_modules(src)

    stale = [m for m in modules if m.startswith(STALE_PREFIX)]
    assert stale == [], (
        f"encoder_cudagraph.py still imports from stale path: {stale}"
    )

    correct = [m for m in modules if m == CORRECT_DEFS]
    assert len(correct) >= 1, (
        "encoder_cudagraph.py must import from "
        "vllm.v1.worker.encoder_cudagraph_defs"
    )


# [pr_diff] fail_to_pass
def test_qwen3_vl_lazy_imports():
    """qwen3_vl.py lazy imports of encoder_cudagraph_defs must use
    correct module path."""
    src = Path(f"{REPO}/vllm/model_executor/models/qwen3_vl.py").read_text()
    modules = _collect_import_from_modules(src)

    stale = [m for m in modules if m.startswith(STALE_PREFIX)]
    assert stale == [], (
        f"qwen3_vl.py still imports from stale path: {stale}"
    )

    correct = [m for m in modules if m == CORRECT_DEFS]
    assert len(correct) >= 3, (
        f"qwen3_vl.py should have at least 3 lazy imports of "
        f"encoder_cudagraph_defs (found {len(correct)})"
    )


# [pr_diff] fail_to_pass
def test_gpu_model_runner_imports():
    """gpu_model_runner.py must import encoder_cudagraph modules from
    vllm.v1.worker."""
    src = Path(f"{REPO}/vllm/v1/worker/gpu_model_runner.py").read_text()
    modules = _collect_import_from_modules(src)

    stale = [m for m in modules if m.startswith(STALE_PREFIX)]
    assert stale == [], (
        f"gpu_model_runner.py still imports from stale path: {stale}"
    )

    correct_defs = [m for m in modules if m == CORRECT_DEFS]
    correct_mgr = [m for m in modules if m == CORRECT_MGR]
    total = len(correct_defs) + len(correct_mgr)
    assert total >= 1, (
        "gpu_model_runner.py must import from "
        "vllm.v1.worker.encoder_cudagraph or "
        "vllm.v1.worker.encoder_cudagraph_defs"
    )


# [pr_diff] fail_to_pass
def test_no_stale_import_paths():
    """No .py file in the codebase should reference the non-existent
    vllm.v1.worker.gpu.mm.encoder_cudagraph path."""
    hits: list[str] = []
    for dirpath, _dirs, files in os.walk(f"{REPO}/vllm"):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            content = Path(fpath).read_text(errors="replace")
            if STALE_PREFIX in content:
                rel = os.path.relpath(fpath, REPO)
                hits.append(rel)

    # Also check tests directory
    for dirpath, _dirs, files in os.walk(f"{REPO}/tests"):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            content = Path(fpath).read_text(errors="replace")
            if STALE_PREFIX in content:
                rel = os.path.relpath(fpath, REPO)
                hits.append(rel)

    assert hits == [], (
        f"Files still reference stale import path "
        f"'{STALE_PREFIX}': {hits}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_encoder_modules_at_correct_location():
    """encoder_cudagraph.py and encoder_cudagraph_defs.py must exist
    at vllm/v1/worker/."""
    ecg = Path(f"{REPO}/vllm/v1/worker/encoder_cudagraph.py")
    ecg_defs = Path(f"{REPO}/vllm/v1/worker/encoder_cudagraph_defs.py")
    assert ecg.exists(), f"Missing {ecg}"
    assert ecg_defs.exists(), f"Missing {ecg_defs}"
    # Verify they are non-trivial (not empty stubs)
    assert ecg.stat().st_size > 500, "encoder_cudagraph.py is suspiciously small"
    assert ecg_defs.stat().st_size > 200, "encoder_cudagraph_defs.py is suspiciously small"
