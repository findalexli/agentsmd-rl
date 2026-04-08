"""
Task: pytorch-sycl-msvc-include-filter
Repo: pytorch/pytorch @ dc12b65cd31ba18cbdc7f2e12e7d1564a67770d0
PR:   #170701

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = Path(f"{REPO}/torch/utils/cpp_extension.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_filter_test(
    icpx_version: str,
    vc_tools_dir: str | None,
    pp_opts: list[str],
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """Extract win_filter_msvc_include_dirs from source and execute it in
    an isolated subprocess with a mocked _get_icpx_version."""
    vc_line = (
        f"os.environ['VCToolsInstallDir'] = {vc_tools_dir!r}"
        if vc_tools_dir is not None
        else "os.environ.pop('VCToolsInstallDir', None)"
    )
    script = "\n".join([
        "import os, ast, textwrap, json",
        "from pathlib import Path",
        "",
        f"source = Path({str(TARGET)!r}).read_text()",
        "tree = ast.parse(source)",
        "",
        "func_src = None",
        "for node in ast.walk(tree):",
        "    if isinstance(node, ast.FunctionDef) and node.name == 'win_filter_msvc_include_dirs':",
        "        func_src = textwrap.dedent(ast.get_source_segment(source, node))",
        "        break",
        "",
        "if func_src is None:",
        "    print(json.dumps({'error': 'function not found'}))",
        "    raise SystemExit(1)",
        "",
        "ns = {'os': os}",
        f"exec(\"def _get_icpx_version(): return {icpx_version!r}\", ns)",
        "exec(func_src, ns)",
        "func = ns['win_filter_msvc_include_dirs']",
        "",
        vc_line,
        f"result = func({pp_opts!r})",
        "print(json.dumps(result))",
    ])
    script_path = Path(REPO) / "_eval_tmp.py"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = TARGET.read_text()
    ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_filter_msvc_paths_new_oneapi():
    """MSVC include paths are filtered out when oneAPI >= 2025.3."""
    opts = [
        "-DSOME_DEFINE",
        r"-IC:\Program Files\Microsoft Visual Studio\2022\Community"
        r"\VC\Tools\MSVC\14.38.33130\include",
        "-I/some/other/path",
        r"-IC:\Program Files\Microsoft Visual Studio\2022\Community"
        r"\VC\Tools\MSVC\14.38.33130\lib",
        "-O2",
    ]
    r = _run_filter_test(
        icpx_version="20250300",
        vc_tools_dir=(
            r"C:\Program Files\Microsoft Visual Studio\2022\Community"
            r"\VC\Tools\MSVC\14.38.33130"
        ),
        pp_opts=opts,
    )
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert len(result) == 3, f"Expected 3 items, got {len(result)}: {result}"
    assert "-DSOME_DEFINE" in result
    assert "-I/some/other/path" in result
    assert "-O2" in result
    for item in result:
        assert "Microsoft Visual Studio" not in item, f"MSVC path not filtered: {item}"


# [pr_diff] fail_to_pass
def test_filter_msvc_paths_newer_oneapi():
    """MSVC include paths are filtered for oneAPI versions above 2025.3 too."""
    opts = [
        "-std:c++17",
        r"-IC:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
        r"\VC\Tools\MSVC\14.40.33807\include",
        "-I/usr/local/include",
    ]
    r = _run_filter_test(
        icpx_version="20260100",
        vc_tools_dir=(
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
            r"\VC\Tools\MSVC\14.40.33807"
        ),
        pp_opts=opts,
    )
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert len(result) == 2, f"Expected 2 items, got {len(result)}: {result}"
    assert "-std:c++17" in result
    assert "-I/usr/local/include" in result


# [pr_diff] fail_to_pass
def test_no_filter_old_oneapi():
    """MSVC paths preserved when oneAPI < 2025.3 (version gating)."""
    opts = [
        "-DSOME_DEFINE",
        r"-IC:\Program Files\Microsoft Visual Studio\2022\Community"
        r"\VC\Tools\MSVC\14.38.33130\include",
        "-I/some/other/path",
        "-O2",
    ]
    r = _run_filter_test(
        icpx_version="20240200",
        vc_tools_dir=(
            r"C:\Program Files\Microsoft Visual Studio\2022\Community"
            r"\VC\Tools\MSVC\14.38.33130"
        ),
        pp_opts=opts,
    )
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result == opts, f"Paths were modified when they shouldn't be: {result}"


# [pr_diff] fail_to_pass
def test_no_filter_without_env_var():
    """Paths preserved when VCToolsInstallDir is not set."""
    opts = [
        "-DSOME_DEFINE",
        r"-IC:\some\msvc\path\include",
        "-I/some/other/path",
    ]
    r = _run_filter_test(
        icpx_version="20250300",
        vc_tools_dir=None,
        pp_opts=opts,
    )
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert len(result) == len(opts), (
        f"Expected {len(opts)} items (no filtering without env var), got {len(result)}"
    )


# [pr_diff] fail_to_pass
def test_filter_empty_opts():
    """Filtering an empty pp_opts list returns empty list."""
    r = _run_filter_test(
        icpx_version="20250300",
        vc_tools_dir=r"C:\VS\VC\Tools\MSVC\14.38",
        pp_opts=[],
    )
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result == [], f"Expected empty list, got: {result}"


# [pr_diff] fail_to_pass
def test_filter_applied_in_sycl_cflags():
    """sycl_cflags construction wraps pp_opts through filter function."""
    source = TARGET.read_text()
    sycl_lines = [
        line.strip()
        for line in source.splitlines()
        if "sycl_cflags" in line and "pp_opts" in line and "=" in line and "common_cflags" in line
    ]
    assert sycl_lines, "Could not find sycl_cflags assignment with pp_opts"
    line = sycl_lines[0]
    assert not re.search(r"\+\s*pp_opts\s*\+", line), (
        f"sycl_cflags still uses raw pp_opts: {line}"
    )
    assert "(" in line and ")" in line, (
        f"pp_opts not wrapped in a function call: {line}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_cuda_hip_flags_preserved():
    """CUDA and HIP flag functions are not removed or broken."""
    source = TARGET.read_text()
    assert "def win_cuda_flags(cflags):" in source, "win_cuda_flags function missing"
    assert "def win_hip_flags(cflags):" in source, "win_hip_flags function missing"


# [static] pass_to_pass
def test_not_stub():
    """Target file retains full cpp_extension module (not stubbed out)."""
    source = TARGET.read_text()
    for sym in [
        "def win_cuda_flags",
        "def win_hip_flags",
        "def win_wrap_ninja_compile",
        "_COMMON_SYCL_FLAGS",
        "sycl_cflags",
    ]:
        assert sym in source, f"Expected symbol missing: {sym}"
    line_count = len(source.splitlines())
    assert line_count >= 2000, f"File has only {line_count} lines — looks like a stub"
