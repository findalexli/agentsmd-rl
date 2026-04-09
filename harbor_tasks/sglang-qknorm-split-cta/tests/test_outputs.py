"""
Task: sglang-qknorm-split-cta
Repo: sgl-project/sglang @ 8a56a7b04d553ecb76fca04eb89bbc20772e2051
PR:   21503

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

f2p tests execute Python analysis scripts via subprocess.
p2p / agent_config tests verify structural invariants inline.
"""

import ast
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = Path(REPO) / "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
_SCRIPT = Path(REPO) / "_eval_tmp.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script in the repo directory."""
    _SCRIPT.write_text(textwrap.dedent(code))
    try:
        return subprocess.run(
            ["python3", str(_SCRIPT)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        _SCRIPT.unlink(missing_ok=True)


def _strip_comments(src: str) -> str:
    """Remove C/C++ block and line comments."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _read_stripped() -> str:
    assert TARGET.exists(), f"{TARGET} does not exist"
    return _strip_comments(TARGET.read_text())


def _read_raw() -> str:
    assert TARGET.exists(), f"{TARGET} does not exist"
    return TARGET.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """Target file must be substantial (>= 80 non-empty lines), not a stub."""
    src = _read_stripped()
    nonempty = sum(1 for line in src.splitlines() if line.strip())
    assert nonempty >= 80, f"Only {nonempty} non-empty lines -- expected >= 80"


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests
# ---------------------------------------------------------------------------

def test_repo_python_syntax():
    """Python files for the JIT kernel module have valid syntax (pass_to_pass)."""
    # Test that norm.py (which loads the .cuh file) has valid Python syntax
    norm_py = Path(REPO) / "python/sglang/jit_kernel/norm.py"
    assert norm_py.exists(), f"{norm_py} does not exist"
    src = norm_py.read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {norm_py}: {e}")


def test_repo_test_file_syntax():
    """Test file for qknorm_across_heads has valid Python syntax (pass_to_pass)."""
    test_py = Path(REPO) / "python/sglang/jit_kernel/tests/test_qknorm_across_heads.py"
    assert test_py.exists(), f"{test_py} does not exist"
    src = test_py.read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {test_py}: {e}")


def test_repo_cuh_header_valid():
    """CUDA header file has valid structure (pass_to_pass)."""
    src = _read_raw()
    # Basic structural checks that don't require compilation
    # Check for balanced braces
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"
    # Check for balanced parentheses
    open_parens = src.count("(")
    close_parens = src.count(")")
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
    # Check file ends with newline
    assert src.endswith("\n"), "File should end with newline"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_blockidx_y_dispatch():
    """Kernel must use blockIdx.y to dispatch between Q and K processing.

    Base code processes both Q and K in a single CTA with no blockIdx.y.
    After fix, blockIdx.y selects which tensor each block handles.
    """
    r = _run_py("""\
        import re, sys
        path = "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
        src = open(path).read()
        src = re.sub(r'/\\*.*?\\*/', '', src, flags=re.DOTALL)
        src = re.sub(r'//[^\\n]*', '', src)

        # Extract the kernel function body
        m = re.search(
            r'__global__\\s+void\\s+qknorm_across_heads_reg_kernel.*?\\{(.+?)^\\}',
            src, re.DOTALL | re.MULTILINE,
        )
        if not m:
            print("FAIL: kernel function body not found")
            sys.exit(1)
        body = m.group(1)

        # blockIdx.y must appear in the kernel body
        refs = re.findall(r'blockIdx\\s*\\.\\s*y', body)
        if not refs:
            print("FAIL: blockIdx.y not found in kernel body")
            sys.exit(1)

        # It must be used to select q vs k (conditional or assignment)
        dispatch = re.search(
            r'blockIdx\\s*\\.\\s*y\\s*==|'
            r'=\\s*.*blockIdx\\s*\\.\\s*y|'
            r'\\?\\s*.*blockIdx\\s*\\.\\s*y|'
            r'blockIdx\\s*\\.\\s*y.*\\?',
            body,
        )
        if not dispatch:
            print(f"FAIL: blockIdx.y found {len(refs)}x but not used for Q/K dispatch")
            sys.exit(1)

        print(f"PASS: blockIdx.y used {len(refs)}x with Q/K dispatch")
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Check failed: {r.stdout.strip()}"


def test_shared_memory_halved():
    """Shared memory must be reduced from 64 to <= 32.

    Base code: __shared__ float shared_memory[64] (32 for Q + 32 for K).
    After fix: only one buffer needed since each CTA handles one tensor.
    """
    r = _run_py("""\
        import re, sys
        path = "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
        src = open(path).read()
        src = re.sub(r'/\\*.*?\\*/', '', src, flags=re.DOTALL)
        src = re.sub(r'//[^\\n]*', '', src)

        matches = re.findall(r'__shared__\\s+float\\s+\\w+\\s*\\[\\s*(\\d+)\\s*\\]', src)
        if not matches:
            print("FAIL: no __shared__ float array found")
            sys.exit(1)

        sizes = [int(m) for m in matches]
        for s in sizes:
            if s > 32:
                print(f"FAIL: shared memory buffer size {s} > 32 (base uses 64)")
                sys.exit(1)

        print(f"PASS: shared memory sizes {sizes}")
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Check failed: {r.stdout.strip()}"


def test_register_vectors_unified():
    """Dual Q/K register vectors must be replaced with unified generic vectors.

    Base code declares 6 vec_t vars: v_q, v_k, v_q_weight, v_k_weight, v_q_out, v_k_out.
    After fix, each CTA handles only one tensor, so <= 3 vec_t vars needed.
    """
    r = _run_py("""\
        import re, sys
        path = "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
        src = open(path).read()
        src = re.sub(r'/\\*.*?\\*/', '', src, flags=re.DOTALL)
        src = re.sub(r'//[^\\n]*', '', src)

        # Extract kernel body to only count declarations inside the kernel
        m = re.search(
            r'__global__\\s+void\\s+qknorm_across_heads_reg_kernel.*?\\{(.+?)^\\}',
            src, re.DOTALL | re.MULTILINE,
        )
        if not m:
            print("FAIL: kernel function body not found")
            sys.exit(1)
        body = m.group(1)

        decls = re.findall(r'\\bvec_t\\s+(\\w+)\\s*;', body)
        if len(decls) > 3:
            print(f"FAIL: {len(decls)} vec_t declarations ({', '.join(decls)}) -- expected <= 3")
            sys.exit(1)

        old_names = {'v_q', 'v_k', 'v_q_weight', 'v_k_weight', 'v_q_out', 'v_k_out'}
        leftover = old_names & set(decls)
        if leftover:
            print(f"FAIL: old dual variable(s) still declared: {leftover}")
            sys.exit(1)

        print(f"PASS: {len(decls)} vec_t declarations: {decls}")
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Check failed: {r.stdout.strip()}"


def test_2d_grid_launch():
    """LaunchKernel must use a 2D grid (dim3 with y=2) instead of 1D.

    Base code: LaunchKernel(static_cast<uint>(N.unwrap()), threads, device.unwrap())
    After fix: dim3(N, 2) to dispatch Q vs K blocks via second dimension.
    """
    r = _run_py("""\
        import re, sys
        path = "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
        src = open(path).read()
        src = re.sub(r'/\\*.*?\\*/', '', src, flags=re.DOTALL)
        src = re.sub(r'//[^\\n]*', '', src)

        # Extract the launcher struct body
        m = re.search(
            r'struct\\s+QKNormAcrossHeadsKernel.*?\\{(.+)',
            src, re.DOTALL,
        )
        if not m:
            print("FAIL: QKNormAcrossHeadsKernel struct not found")
            sys.exit(1)
        launcher = m.group(1)

        # Must use dim3 with y=2 in the LaunchKernel call
        if not re.search(r'dim3\\s*[\\({]\\s*[^,]+,\\s*2\\s*[\\)}]', launcher):
            print("FAIL: no 2D grid launch (dim3 with y=2) in launcher")
            sys.exit(1)

        # Verify LaunchKernel is the launch mechanism (not raw <<<>>>)
        if not re.search(r'\\bLaunchKernel\\b', launcher):
            print("FAIL: LaunchKernel not found in launcher")
            sys.exit(1)

        print("PASS: 2D grid launch with dim3(N, 2) found")
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Check failed: {r.stdout.strip()}"


def test_rms_const_params():
    """rms() helper parameters must be const-qualified (read-only).

    Base: rms(packed_t& val, packed_t& weight, float rsqrt_square_sum)
    Fix:  rms(const packed_t& val, const packed_t& weight, ...)
    """
    r = _run_py("""\
        import re, sys
        path = "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
        src = open(path).read()
        src = re.sub(r'/\\*.*?\\*/', '', src, flags=re.DOTALL)
        src = re.sub(r'//[^\\n]*', '', src)

        # Find the rms function definition signature
        m = re.search(r'\\brms\\s*\\(([^)]+)\\)', src)
        if not m:
            print("FAIL: rms() function signature not found")
            sys.exit(1)

        params = [p.strip() for p in m.group(1).split(',')]
        const_ref_params = [p for p in params if 'const' in p and '&' in p]
        if len(const_ref_params) < 2:
            print(f"FAIL: only {len(const_ref_params)} const-ref param(s), expected >= 2")
            sys.exit(1)

        print(f"PASS: {len(const_ref_params)} const-ref params in rms()")
    """)
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Check failed: {r.stdout.strip()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression checks
# ---------------------------------------------------------------------------

def test_rms_helper_exists():
    """rms() helper function must still exist with a real body (not removed)."""
    src = _read_stripped()
    assert re.search(r"\brms\s*\(", src), "rms() function not found"
    assert re.search(r"\brms\s*\([^)]*\)\s*\{[^}]+\}", src, re.DOTALL), (
        "rms() function has no body"
    )


def test_launcher_struct_exists():
    """QKNormAcrossHeadsKernel struct with run() method must still exist."""
    src = _read_stripped()
    assert re.search(r"struct\s+QKNormAcrossHeadsKernel", src), (
        "QKNormAcrossHeadsKernel struct not found"
    )
    assert re.search(r"\bvoid\s+run\s*\(", src), (
        "run() method not found in launcher struct"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- from .claude/skills/add-jit-kernel/SKILL.md
# ---------------------------------------------------------------------------

def test_sgl_device_macro():
    """Device helper functions must use SGL_DEVICE macro (not raw __device__).

    SKILL.md line 51: "SGL_DEVICE -- Expands to __forceinline__ __device__."
    """
    src = _read_raw()
    rms_match = re.search(r"SGL_DEVICE\s+\w+\s+rms\s*\(", src)
    assert rms_match, "rms() function must use SGL_DEVICE macro"


def test_uses_launch_kernel():
    """Kernel must be launched via LaunchKernel helper, not raw <<<>>> syntax.

    SKILL.md line 300: "Use LaunchKernel -- it resolves the stream and checks errors."
    """
    src = _read_stripped()
    assert re.search(r"\bLaunchKernel\b", src), "LaunchKernel not found"
    assert not re.search(r"<<<.*>>>", src), "Raw <<<>>> kernel launch found"


def test_device_cast_used():
    """Type conversions must use device::cast, not raw C-style casts.

    SKILL.md line 304: "device::cast<To, From> for cross-type conversions."
    """
    src = _read_stripped()
    kernel_match = re.search(
        r"__global__\s+void\s+qknorm_across_heads_reg_kernel.*?\{(.+?)^struct",
        src, re.DOTALL | re.MULTILINE,
    )
    assert kernel_match, "Kernel function body not found"
    kernel_body = kernel_match.group(1)
    casts = re.findall(r"device::cast\s*<", kernel_body)
    assert len(casts) >= 1, "No device::cast<> found in kernel body"


def test_syncthreads_after_smem_write():
    """__syncthreads() must be called after writing to shared memory before reading.

    SKILL.md line 156: "Caller is responsible for __syncthreads() after if the result
    in smem[0] is needed."
    """
    src = _read_stripped()
    assert re.search(r"__syncthreads\s*\(\s*\)", src), (
        "No __syncthreads() found"
    )
    syncs = re.findall(r"__syncthreads\s*\(\s*\)", src)
    assert len(syncs) >= 2, (
        f"Only {len(syncs)} __syncthreads() -- expected >= 2 for shared memory coordination"
    )
