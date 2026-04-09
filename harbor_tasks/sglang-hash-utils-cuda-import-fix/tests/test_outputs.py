"""
Task: sglang-hash-utils-cuda-import-fix
Repo: sgl-project/sglang @ 5e2b0f860c020bfa49ad280203b98941500757f1
PR:   22214

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import hashlib
import inspect
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import List, Optional

import pytest

REPO = "/workspace/sglang"


def _extract_function_source(file_path: Path, func_name: str) -> str:
    """Extract a function's source code from a file using AST."""
    src = file_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            # Get the source lines for this function
            start_line = node.lineno
            end_line = node.end_lineno
            lines = src.split('\n')
            func_lines = lines[start_line - 1:end_line]
            return '\n'.join(func_lines)
    return None


def _extract_and_compile_function(file_path: Path, func_name: str):
    """Extract a function from file and compile it for execution."""
    func_src = _extract_function_source(file_path, func_name)
    if func_src is None:
        return None

    # Dedent the function source
    func_src = textwrap.dedent(func_src)

    # Compile and execute in a restricted namespace with necessary imports
    namespace = {
        'hashlib': hashlib,
        'List': List,
        'Optional': Optional,
    }

    try:
        code = compile(func_src, f"<{func_name}>", "exec")
        exec(code, namespace)
        return namespace.get(func_name)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files_to_check = [
        "python/sglang/srt/managers/cache_controller.py",
        "python/sglang/srt/mem_cache/hicache_storage.py",
        "python/sglang/srt/mem_cache/radix_cache.py",
        "python/sglang/srt/mem_cache/utils.py",
    ]

    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        if full_path.exists():
            src = full_path.read_text()
            try:
                ast.parse(src)
            except SyntaxError as e:
                raise AssertionError(f"Syntax error in {file_path}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_import_hash_utils_from_utils():
    """Hash functions can be imported from utils module (lightweight, no CUDA deps)."""
    # On base commit: utils.py doesn't have these functions → functions not found
    # On fix: utils.py has these functions → extraction succeeds
    utils_path = Path(REPO) / "python/sglang/srt/mem_cache/utils.py"

    get_hash_str = _extract_and_compile_function(utils_path, "get_hash_str")
    hash_str_to_int64 = _extract_and_compile_function(utils_path, "hash_str_to_int64")

    assert get_hash_str is not None, "get_hash_str not found in utils.py"
    assert hash_str_to_int64 is not None, "hash_str_to_int64 not found in utils.py"
    assert callable(get_hash_str), "get_hash_str should be callable"
    assert callable(hash_str_to_int64), "hash_str_to_int64 should be callable"


# [pr_diff] fail_to_pass
def test_hash_functions_correctness():
    """Hash functions produce expected output."""
    utils_path = Path(REPO) / "python/sglang/srt/mem_cache/utils.py"

    get_hash_str = _extract_and_compile_function(utils_path, "get_hash_str")
    hash_str_to_int64 = _extract_and_compile_function(utils_path, "hash_str_to_int64")

    assert get_hash_str is not None, "get_hash_str not found in utils.py"
    assert hash_str_to_int64 is not None, "hash_str_to_int64 not found in utils.py"

    # Test get_hash_str with single tokens
    tokens = [1, 2, 3]
    result = get_hash_str(tokens)
    # Verify against manual computation
    hasher = hashlib.sha256()
    for t in tokens:
        hasher.update(t.to_bytes(4, byteorder="little", signed=False))
    expected = hasher.hexdigest()
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with prior_hash
    prior = result
    tokens2 = [4, 5]
    result2 = get_hash_str(tokens2, prior)
    hasher2 = hashlib.sha256()
    hasher2.update(bytes.fromhex(prior))
    for t in tokens2:
        hasher2.update(t.to_bytes(4, byteorder="little", signed=False))
    expected2 = hasher2.hexdigest()
    assert result2 == expected2, f"Expected {expected2}, got {result2}"

    # Test hash_str_to_int64
    test_hash = "aabbccdd11223344000000000000000000000000000000000000000000000000"
    int_result = hash_str_to_int64(test_hash)
    # First 16 hex chars: aabbccdd11223344
    uint64_val = int("aabbccdd11223344", 16)
    if uint64_val >= 2**63:
        expected_int = uint64_val - 2**64
    else:
        expected_int = uint64_val
    assert int_result == expected_int, f"Expected {expected_int}, got {int_result}"


# [pr_diff] fail_to_pass
def test_hash_bigram_mode():
    """Hash function supports EAGLE bigram mode with tuple tokens."""
    utils_path = Path(REPO) / "python/sglang/srt/mem_cache/utils.py"

    get_hash_str = _extract_and_compile_function(utils_path, "get_hash_str")
    assert get_hash_str is not None, "get_hash_str not found in utils.py"

    # Test with bigram tuples (EAGLE mode)
    tokens = [(1, 2), (3, 4)]
    result = get_hash_str(tokens)

    # Verify against manual computation
    hasher = hashlib.sha256()
    for t in tokens:
        if isinstance(t, tuple):
            for elem in t:
                hasher.update(elem.to_bytes(4, byteorder="little", signed=False))
        else:
            hasher.update(t.to_bytes(4, byteorder="little", signed=False))
    expected = hasher.hexdigest()
    assert result == expected, f"Expected {expected}, got {result}"


# [pr_diff] fail_to_pass
def test_import_sites_updated():
    """Import sites use utils module instead of hicache_storage."""
    # Check that radix_cache.py imports from utils, not hicache_storage
    radix_cache_path = Path(REPO) / "python/sglang/srt/mem_cache/radix_cache.py"
    content = radix_cache_path.read_text()

    # Should import from utils now
    assert "from sglang.srt.mem_cache.utils import get_hash_str" in content, \
        "radix_cache.py should import get_hash_str from utils module"
    assert "from sglang.srt.mem_cache.utils import" in content and "hash_str_to_int64" in content, \
        "radix_cache.py should import hash_str_to_int64 from utils module"

    # Check cache_controller.py
    cache_controller_path = Path(REPO) / "python/sglang/srt/managers/cache_controller.py"
    cc_content = cache_controller_path.read_text()

    assert "from sglang.srt.mem_cache.utils import get_hash_str" in cc_content, \
        "cache_controller.py should import get_hash_str from utils module"


# [pr_diff] fail_to_pass
def test_hicache_storage_functions_removed():
    """Hash functions are removed from hicache_storage module."""
    hicache_path = Path(REPO) / "python/sglang/srt/mem_cache/hicache_storage.py"
    content = hicache_path.read_text()

    # These functions should no longer be defined here (moved to utils.py)
    assert "def get_hash_str(" not in content, \
        "get_hash_str should be removed from hicache_storage.py"
    assert "def hash_str_to_int64(" not in content, \
        "hash_str_to_int64 should be removed from hicache_storage.py"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """New hash functions have real implementation logic."""
    utils_path = Path(REPO) / "python/sglang/srt/mem_cache/utils.py"
    content = utils_path.read_text()
    tree = ast.parse(content)

    found_get_hash_str = False
    found_hash_str_to_int64 = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "get_hash_str":
                # Check it has meaningful statements (not just pass/return None)
                stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
                # Should have hasher creation, loop, return
                assert len(stmts) >= 3, "get_hash_str body is too short (likely a stub)"
                found_get_hash_str = True
            elif node.name == "hash_str_to_int64":
                stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
                # Should have int conversion, conditional, return
                assert len(stmts) >= 3, "hash_str_to_int64 body is too short (likely a stub)"
                found_hash_str_to_int64 = True

    assert found_get_hash_str, "get_hash_str function not found in utils.py"
    assert found_hash_str_to_int64, "hash_str_to_int64 function not found in utils.py"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_modified_files_syntax():
    """Modified Python files must have valid syntax (repo CI check)."""
    files_to_check = [
        "python/sglang/srt/managers/cache_controller.py",
        "python/sglang/srt/mem_cache/hicache_storage.py",
        "python/sglang/srt/mem_cache/radix_cache.py",
        "python/sglang/srt/mem_cache/utils.py",
    ]

    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        if full_path.exists():
            # Use py_compile for syntax checking
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(full_path)],
                capture_output=True, text=True, timeout=30, cwd=REPO,
            )
            assert r.returncode == 0, f"Syntax error in {file_path}:\\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_modified_files_lint():
    """Modified Python files must pass ruff syntax/import checks (repo CI check)."""
    files_to_check = [
        "python/sglang/srt/managers/cache_controller.py",
        "python/sglang/srt/mem_cache/hicache_storage.py",
        "python/sglang/srt/mem_cache/radix_cache.py",
        "python/sglang/srt/mem_cache/utils.py",
    ]

    # Check ruff is available, skip if not
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "--version"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        pytest.skip("ruff not available, skipping lint check")

    # Run ruff with syntax and import error checks only
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select=E9,F821"] +
        files_to_check,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint errors:\\n{r.stdout}\\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_hash_functions_work_on_base():
    """Hash functions produce correct output on base commit (repo CI regression)."""
    import hashlib

    # Read the function source from hicache_storage.py (base commit location)
    hicache_path = Path(REPO) / "python/sglang/srt/mem_cache/hicache_storage.py"
    content = hicache_path.read_text()

    # Check functions exist and can be executed via AST extraction
    get_hash_str = _extract_and_compile_function(hicache_path, "get_hash_str")
    hash_str_to_int64 = _extract_and_compile_function(hicache_path, "hash_str_to_int64")

    if get_hash_str is None or hash_str_to_int64 is None:
        # Functions might already be moved to utils.py (after fix)
        utils_path = Path(REPO) / "python/sglang/srt/mem_cache/utils.py"
        get_hash_str = _extract_and_compile_function(utils_path, "get_hash_str")
        hash_str_to_int64 = _extract_and_compile_function(utils_path, "hash_str_to_int64")

    assert get_hash_str is not None, "get_hash_str not found in expected locations"
    assert hash_str_to_int64 is not None, "hash_str_to_int64 not found in expected locations"

    # Test get_hash_str with single tokens
    tokens = [1, 2, 3]
    result = get_hash_str(tokens)

    # Verify against manual computation
    hasher = hashlib.sha256()
    for t in tokens:
        hasher.update(t.to_bytes(4, byteorder="little", signed=False))
    expected = hasher.hexdigest()
    assert result == expected, f"get_hash_str failed: expected {expected}, got {result}"

    # Test hash_str_to_int64
    test_hash = "aabbccdd11223344000000000000000000000000000000000000000000000000"
    int_result = hash_str_to_int64(test_hash)
    uint64_val = int("aabbccdd11223344", 16)
    expected_int = uint64_val - 2**64 if uint64_val >= 2**63 else uint64_val
    assert int_result == expected_int, f"hash_str_to_int64 failed: expected {expected_int}, got {int_result}"

    # Test bigram mode
    tokens_bigram = [(1, 2), (3, 4)]
    result_bigram = get_hash_str(tokens_bigram)
    hasher2 = hashlib.sha256()
    for t in tokens_bigram:
        if isinstance(t, tuple):
            for elem in t:
                hasher2.update(elem.to_bytes(4, byteorder="little", signed=False))
        else:
            hasher2.update(t.to_bytes(4, byteorder="little", signed=False))
    expected_bigram = hasher2.hexdigest()
    assert result_bigram == expected_bigram, f"get_hash_str bigram failed: expected {expected_bigram}, got {result_bigram}"
