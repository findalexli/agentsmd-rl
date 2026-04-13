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

P2P CI commands tested and confirmed working in Docker:
- ruff check (already present)
- typos spell check
- Python syntax check (py_compile, already present)
- SPDX header check
- Forbidden imports check
- Boolean context manager check
- Init lazy imports check
- torch.cuda API prevention check
- Attention backend docs check
- YAML syntax validation
"""

import ast
import os
import subprocess
import sys
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
# Pass-to-pass (repo_tests)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's Python linting passes on modified files (pass_to_pass)."""
    # Install ruff if not available
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff", "-q"],
            capture_output=True, check=True,
        )

    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/encoder_cudagraph_defs.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
        f"{REPO}/vllm/model_executor/models/interfaces.py",
        f"{REPO}/vllm/model_executor/models/qwen3_vl.py",
        f"{REPO}/tests/v1/cudagraph/test_encoder_cudagraph.py",
    ]
    r = subprocess.run(
        ["ruff", "check", "--output-format=github"] + files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_typos():
    """Repo's spell check (typos) passes on modified files (pass_to_pass)."""
    # Install typos if not available
    try:
        subprocess.run(["typos", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "typos", "-q"],
            capture_output=True, check=True,
        )

    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/encoder_cudagraph_defs.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
        f"{REPO}/vllm/model_executor/models/interfaces.py",
        f"{REPO}/vllm/model_executor/models/qwen3_vl.py",
        f"{REPO}/tests/v1/cudagraph/test_encoder_cudagraph.py",
    ]
    r = subprocess.run(
        ["typos"] + files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    """Python syntax is valid for all modified files (pass_to_pass)."""
    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/encoder_cudagraph_defs.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
        f"{REPO}/vllm/model_executor/models/interfaces.py",
        f"{REPO}/vllm/model_executor/models/qwen3_vl.py",
        f"{REPO}/tests/v1/cudagraph/test_encoder_cudagraph.py",
    ]
    r = subprocess.run(
        ["python", "-m", "py_compile"] + files,
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_spdx_headers():
    """Repo's SPDX license headers check passes on modified files (pass_to_pass)."""
    # Install regex if not available
    try:
        import regex  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "regex", "-q"],
            capture_output=True, check=True,
        )

    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/encoder_cudagraph_defs.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
        f"{REPO}/vllm/model_executor/models/interfaces.py",
        f"{REPO}/vllm/model_executor/models/qwen3_vl.py",
        f"{REPO}/tests/v1/cudagraph/test_encoder_cudagraph.py",
    ]
    r = subprocess.run(
        [sys.executable, f"{REPO}/tools/pre_commit/check_spdx_header.py"] + files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"SPDX header check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_forbidden_imports():
    """Repo's forbidden imports check passes on worker files (pass_to_pass)."""
    try:
        import regex  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "regex", "-q"],
            capture_output=True, check=True,
        )

    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
    ]
    r = subprocess.run(
        [sys.executable, f"{REPO}/tools/pre_commit/check_forbidden_imports.py"] + files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Forbidden imports check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_boolean_context_manager():
    """Repo's boolean context manager check passes on modified files (pass_to_pass)."""
    try:
        import regex  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "regex", "-q"],
            capture_output=True, check=True,
        )

    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
        f"{REPO}/vllm/model_executor/models/qwen3_vl.py",
    ]
    r = subprocess.run(
        [sys.executable, f"{REPO}/tools/pre_commit/check_boolean_context_manager.py"] + files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Boolean context manager check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_init_lazy_imports():
    """Repo's root init lazy imports check passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, f"{REPO}/tools/pre_commit/check_init_lazy_imports.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Init lazy imports check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_no_torch_cuda_calls():
    """Repo's torch.cuda API prevention check passes on worker files (pass_to_pass)."""
    try:
        import regex  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "regex", "-q"],
            capture_output=True, check=True,
        )

    files = [
        f"{REPO}/vllm/v1/worker/encoder_cudagraph.py",
        f"{REPO}/vllm/v1/worker/gpu_model_runner.py",
    ]
    r = subprocess.run(
        [sys.executable, f"{REPO}/tools/pre_commit/check_torch_cuda.py"] + files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"torch.cuda check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_attention_backend_docs():
    """Repo's attention backend documentation is up to date (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, f"{REPO}/tools/pre_commit/generate_attention_backend_docs.py", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Attention backend docs check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yaml_syntax():
    """YAML workflow files have valid syntax (pass_to_pass)."""
    try:
        import yaml  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyyaml", "-q"],
            capture_output=True, check=True,
        )

    yaml_files = [
        f"{REPO}/.github/workflows/pre-commit.yml",
        f"{REPO}/.pre-commit-config.yaml",
    ]
    for f in yaml_files:
        r = subprocess.run(
            [sys.executable, "-c", f"import yaml; yaml.safe_load(open('{f}'))"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"YAML syntax error in {f}:\n{r.stderr}"


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
