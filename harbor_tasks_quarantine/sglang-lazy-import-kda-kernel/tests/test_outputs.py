"""
Task: sglang-lazy-import-kda-kernel
Repo: sgl-project/sglang @ 75682f1d2f60797fb438da8fd6fe40e92e1a26fe
PR:   21428

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/srt/layers/attention/linear/kda_backend.py"
TARGET_REL = "python/sglang/srt/layers/attention/linear/kda_backend.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """kda_backend.py must parse without syntax errors."""
    src = Path(TARGET).read_text()
    ast.parse(src)


# [repo_tests] pass_to_pass
def test_repo_syntax_compile():
    """Python syntax compilation check via py_compile (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Ruff linter check on kda_backend.py passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", TARGET_REL],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Black formatting check on kda_backend.py passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "black", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", TARGET_REL],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """isort import ordering check on kda_backend.py passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "isort", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", TARGET_REL],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """codespell spelling check on kda_backend.py passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "codespell", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["codespell", "--config", ".codespellrc", TARGET_REL],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_import_structure():
    """AST structure check - file must be parseable and have expected structure (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c",
         f"import ast; tree = ast.parse(open('{TARGET}').read()); "
         f"classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]; "
         f"assert 'KDAKernelDispatcher' in classes, 'KDAKernelDispatcher class missing'; "
         f"print('AST structure OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST structure check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_file_not_empty():
    """File must have substantial content (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c",
         f"src = open('{TARGET}').read(); "
         f"lines = src.strip().splitlines(); "
         f"assert len(lines) >= 20, f'Too few lines: {{len(lines)}}'; "
         f"assert 'class KDAKernelDispatcher' in src, 'KDAKernelDispatcher class not found'; "
         f"print('File has expected content')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"File content check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_no_wildcard_imports():
    """File should not use wildcard imports (repo code style check) (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c",
         "import ast; "
         f"tree = ast.parse(open('{TARGET}').read()); "
         "wildcard_imports = [(n.lineno, alias.name) for n in ast.walk(tree) "
         "if isinstance(n, ast.ImportFrom) for alias in n.names if alias.name == '*']; "
         "assert not wildcard_imports, f'Wildcard imports found: {wildcard_imports}'; "
         "print('No wildcard imports')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Wildcard import check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_import_kda_backend_no_cuda_crash():
    """Importing kda_backend must not crash with a 'cuda' ModuleNotFoundError.

    The base commit has a top-level import that chains to cuda.bindings.driver,
    crashing on non-CUDA (AMD/ROCm/CPU) platforms. The fix makes it lazy.
    """
    script = (
        "import sys\n"
        "sys.path.insert(0, '/workspace/sglang/python')\n"
        "try:\n"
        "    from sglang.srt.layers.attention.linear import kda_backend\n"
        "except ModuleNotFoundError as e:\n"
        "    if 'cuda' in str(e).lower() or 'kda_cutedsl' in str(e).lower():\n"
        "        print(f'FAIL: {e}')\n"
        "        sys.exit(1)\n"
        "except ImportError as e:\n"
        "    if 'cuda' in str(e).lower():\n"
        "        print(f'FAIL: {e}')\n"
        "        sys.exit(1)\n"
    )
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"CUDA-related import error at module load:\n{r.stdout}\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_cutedsl_import_not_at_module_level():
    """CuteDSLKDAKernel must not be imported at module level.

    A bare top-level `from ...kda_cutedsl import CuteDSLKDAKernel` eagerly
    loads CUDA-only code. The import must be deferred (lazy local import,
    conditional guard, or similar).
    """
    # AST-only because: CuteDSLKDAKernel chains to cuda.bindings.driver which
    # requires CUDA hardware; cannot be imported on CPU-only test containers.
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom):
            names = [alias.name for alias in node.names]
            assert "CuteDSLKDAKernel" not in names, (
                f"CuteDSLKDAKernel is imported at module level (line {node.lineno}), "
                "which crashes on non-CUDA platforms"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dispatcher_class_intact():
    """KDAKernelDispatcher class must exist with __init__ and key attributes."""
    # AST-only because: instantiating KDAKernelDispatcher requires torch, CUDA
    # runtime, and complex attention backend objects not available on CPU
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    classes = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    assert "KDAKernelDispatcher" in classes, "KDAKernelDispatcher class missing"
    methods = [
        n.name for n in ast.walk(classes["KDAKernelDispatcher"])
        if isinstance(n, ast.FunctionDef)
    ]
    assert "__init__" in methods, "KDAKernelDispatcher.__init__ missing"


# [static] pass_to_pass
def test_cutedsl_still_referenced():
    """CuteDSLKDAKernel must still be referenced (not deleted entirely)."""
    src = Path(TARGET).read_text()
    assert "CuteDSLKDAKernel" in src, (
        "CuteDSLKDAKernel not found anywhere in file -- import was deleted "
        "instead of being made lazy"
    )


# [static] pass_to_pass
def test_triton_import_still_toplevel():
    """TritonKDAKernel must remain a top-level import (unchanged by fix).

    Only the CuteDSL import should be lazified; TritonKDAKernel is always
    needed and must stay at module level.
    """
    # AST-only because: TritonKDAKernel depends on triton which is not
    # installed in the CPU-only test container
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    found = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "kda_triton" in node.module:
            names = [alias.name for alias in node.names]
            if "TritonKDAKernel" in names:
                found = True
                break
    assert found, (
        "TritonKDAKernel top-level import was removed -- "
        "only CuteDSLKDAKernel should be lazified"
    )


# [static] pass_to_pass
def test_not_stub():
    """File must have real content, not be gutted or stubbed out."""
    src = Path(TARGET).read_text()
    lines = src.strip().splitlines()
    assert len(lines) >= 30, f"File too short ({len(lines)} lines), likely a stub"
    for ident in ("TritonKDAKernel", "decode_kernel", "is_cuda", "is_cutedsl"):
        assert ident in src, f"Required identifier '{ident}' missing from file"
