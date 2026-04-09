"""
Task: vllm-cuda13-swap-blocks-compile
Repo: vllm @ 81994e1d0ea6e0486cfbdad02e00942614c55264
PR:   38915

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests use subprocess.run() to execute Python code that performs
behavioral validation of the CUDA source file changes.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/vllm"
CACHE_KERNELS = Path(REPO) / "csrc" / "cache_kernels.cu"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_swap_blocks_batch_exists():
    """swap_blocks_batch function must still be defined."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()
if not re.search(r'void\\s+swap_blocks_batch\\s*\\(', content):
    print("FAIL: swap_blocks_batch function definition not found")
    exit(1)
print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_memcpy_batch_async_still_used():
    """cuMemcpyBatchAsync must still be called within swap_blocks_batch."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()
start = content.find("void swap_blocks_batch(")
assert start != -1, "swap_blocks_batch function not found"
func_body = content[start:start + 4000]
if 'cuMemcpyBatchAsync' not in func_body:
    print("FAIL: cuMemcpyBatchAsync should still be called in swap_blocks_batch")
    exit(1)
print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess.run()
# ---------------------------------------------------------------------------

def test_cuda13_version_conditional():
    """swap_blocks_batch must have a CUDA 13 version guard to handle the
    changed cuMemcpyBatchAsync API signature in CUDA 13."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()
start = content.find("void swap_blocks_batch(")
assert start != -1, "swap_blocks_batch function not found"
func_body = content[start:start + 4000]

has_guard = bool(re.search(r'CUDA_VERSION\\s*>=\\s*13000', func_body)) or \\
            bool(re.search(r'__CUDACC_VER_MAJOR__\\s*>=\\s*13', func_body))
if not has_guard:
    print("FAIL: Missing CUDA 13 version conditional in swap_blocks_batch")
    exit(1)
print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_dual_memcpy_batch_paths():
    """swap_blocks_batch needs two separate cuMemcpyBatchAsync call sites
    to handle both CUDA 13+ (8-arg) and older CUDA (9-arg) API signatures."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()
start = content.find("void swap_blocks_batch(")
assert start != -1, "swap_blocks_batch function not found"
func_body = content[start:start + 4000]

calls = re.findall(r'cuMemcpyBatchAsync\\s*\\(', func_body)
if len(calls) < 2:
    print(f"FAIL: Expected >=2 cuMemcpyBatchAsync calls, found {len(calls)}")
    exit(1)
print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_cuda13_branch_no_fail_idx():
    """The CUDA 13+ code path must NOT pass fail_idx to cuMemcpyBatchAsync,
    as CUDA 13 removed that parameter from the API."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()
start = content.find("void swap_blocks_batch(")
assert start != -1, "swap_blocks_batch function not found"
func_body = content[start:start + 4000]

match = re.search(
    r'(?:CUDA_VERSION\\s*>=\\s*13000|__CUDACC_VER_MAJOR__\\s*>=\\s*13)'
    r'(.*?)#\\s*(?:else|endif)',
    func_body, re.DOTALL
)
if not match:
    print("FAIL: CUDA 13+ conditional block not found in swap_blocks_batch")
    exit(1)

cuda13_block = match.group(1)
if 'cuMemcpyBatchAsync' not in cuda13_block:
    print("FAIL: cuMemcpyBatchAsync not called in the CUDA 13+ branch")
    exit(1)

if 'fail_idx' in cuda13_block:
    print("FAIL: CUDA 13+ branch must not reference fail_idx")
    exit(1)

print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_mutable_data_ptr_usage():
    """The fix must use mutable_data_ptr() instead of const data_ptr() + const_cast
    to handle the non-const pointer requirements for cuMemcpyBatchAsync."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()
start = content.find("void swap_blocks_batch(")
assert start != -1, "swap_blocks_batch function not found"
func_body = content[start:start + 4000]

has_mutable = 'mutable_data_ptr' in func_body

if not has_mutable:
    print("FAIL: swap_blocks_batch should use mutable_data_ptr()")
    exit(1)

# If old const_cast pattern exists, it should only be in the else branch (older CUDA)
has_old_const_cast = 'const_cast<int64_t*>' in func_body
if has_old_const_cast:
    match = re.search(
        r'(?:CUDA_VERSION\\s*>=\\s*13000|__CUDACC_VER_MAJOR__\\s*>=\\s*13)'
        r'(.*?)#\\s*(?:else|endif)',
        func_body, re.DOTALL
    )
    if match and 'const_cast' in match.group(1):
        print("FAIL: CUDA 13+ branch should not use const_cast")
        exit(1)

print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-Pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

def test_repo_source_valid_cpp_syntax():
    """Source file must have balanced braces and valid C++ structure."""
    code = """
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()

open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    print(f"FAIL: Unbalanced braces: {open_braces} open, {close_braces} close")
    exit(1)

open_parens = content.count('(')
close_parens = content.count(')')
if open_parens != close_parens:
    print(f"FAIL: Unbalanced parentheses: {open_parens} open, {close_parens} close")
    exit(1)

print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_repo_includes_cuda_headers():
    """Source must include necessary CUDA/ROCm headers (pass_to_pass)."""
    code = """
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()

has_cuda = '#include <cuda.h>' in content or '#include "cuda' in content
has_rocm = '#include <hip/hip' in content or 'USE_ROCM' in content
has_torch = '#include <torch/' in content or '#include "torch' in content

if not has_torch:
    print("FAIL: Must include torch headers")
    exit(1)

if not (has_cuda or has_rocm):
    print("FAIL: Must include CUDA or ROCm headers")
    exit(1)

print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_repo_swap_blocks_signature():
    """swap_blocks_batch must have correct function signature (pass_to_pass)."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()

pattern = r'void\\s+swap_blocks_batch\\s*\\(\\s*const\\s+torch::Tensor&\\s+src_ptrs\\s*,\\s*const\\s+torch::Tensor&\\s+dst_ptrs\\s*,\\s*const\\s+torch::Tensor&\\s+sizes\\s*\\)'
match = re.search(pattern, content)
if not match:
    print("FAIL: swap_blocks_batch must have correct signature with const torch::Tensor& parameters")
    exit(1)

print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout


def test_repo_no_syntax_errors():
    """Source file must not contain obvious syntax errors (pass_to_pass)."""
    code = """
import re
from pathlib import Path
content = Path('""" + str(CACHE_KERNELS) + """').read_text()

lines = content.split('\\n')
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('#') or stripped.startswith('//'):
        continue
    if ';;;' in stripped:
        print(f"FAIL: Line {i} has triple semicolon, possible syntax error")
        exit(1)

print("PASS")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout
