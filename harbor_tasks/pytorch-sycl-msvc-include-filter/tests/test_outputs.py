"""
Task: pytorch-sycl-msvc-include-filter
Repo: pytorch/pytorch @ dc12b65cd31ba18cbdc7f2e12e7d1564a67770d0
PR:   #170701

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import re
import sys
import textwrap
from pathlib import Path

TARGET = Path("/workspace/pytorch/torch/utils/cpp_extension.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_filter_func():
    """Find and return (name, dedented_source) of the MSVC filter function."""
    source = TARGET.read_text()
    tree = ast.parse(source)
    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            src = ast.get_source_segment(source, node)
            if src and "VCToolsInstallDir" in src and "pp_opts" in src:
                candidates.append((node.name, textwrap.dedent(src)))
    if not candidates:
        return None, None
    # Return the shortest match (innermost function, not the enclosing parent)
    return min(candidates, key=lambda x: len(x[1]))


def _exec_filter_func(icpx_version: str):
    """Build and return the filter function with a mocked _get_icpx_version."""
    name, src = _find_filter_func()
    assert name is not None, "No function found that filters MSVC include dirs from pp_opts"
    env = {}
    exec(
        f"import os\ndef _get_icpx_version():\n    return \"{icpx_version}\"\n\n{src}",
        env,
    )
    return env[name]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = TARGET.read_text()
    ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_msvc_paths_new_oneapi():
    """MSVC include paths are filtered out when oneAPI >= 2025.3."""
    func = _exec_filter_func("20250300")
    os.environ["VCToolsInstallDir"] = (
        r"C:\Program Files\Microsoft Visual Studio\2022\Community"
        r"\VC\Tools\MSVC\14.38.33130"
    )
    try:
        opts = [
            "-DSOME_DEFINE",
            r"-IC:\Program Files\Microsoft Visual Studio\2022\Community"
            r"\VC\Tools\MSVC\14.38.33130\include",
            "-I/some/other/path",
            r"-IC:\Program Files\Microsoft Visual Studio\2022\Community"
            r"\VC\Tools\MSVC\14.38.33130\lib",
            "-O2",
        ]
        result = func(opts)
        # MSVC paths should be gone, 3 items remain
        assert len(result) == 3, f"Expected 3 items, got {len(result)}: {result}"
        assert "-DSOME_DEFINE" in result
        assert "-I/some/other/path" in result
        assert "-O2" in result
        for item in result:
            assert "Microsoft Visual Studio" not in item, f"MSVC path not filtered: {item}"
    finally:
        os.environ.pop("VCToolsInstallDir", None)


# [pr_diff] fail_to_pass
def test_filter_msvc_paths_newer_oneapi():
    """MSVC include paths are filtered for oneAPI versions above 2025.3 too."""
    func = _exec_filter_func("20260100")
    os.environ["VCToolsInstallDir"] = (
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
        r"\VC\Tools\MSVC\14.40.33807"
    )
    try:
        opts = [
            "-std:c++17",
            r"-IC:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
            r"\VC\Tools\MSVC\14.40.33807\include",
            "-I/usr/local/include",
        ]
        result = func(opts)
        assert len(result) == 2, f"Expected 2 items, got {len(result)}: {result}"
        assert "-std:c++17" in result
        assert "-I/usr/local/include" in result
    finally:
        os.environ.pop("VCToolsInstallDir", None)


# [pr_diff] fail_to_pass
def test_no_filter_old_oneapi():
    """MSVC paths preserved when oneAPI < 2025.3 (version gating)."""
    func = _exec_filter_func("20240200")
    os.environ["VCToolsInstallDir"] = (
        r"C:\Program Files\Microsoft Visual Studio\2022\Community"
        r"\VC\Tools\MSVC\14.38.33130"
    )
    try:
        opts = [
            "-DSOME_DEFINE",
            r"-IC:\Program Files\Microsoft Visual Studio\2022\Community"
            r"\VC\Tools\MSVC\14.38.33130\include",
            "-I/some/other/path",
            "-O2",
        ]
        result = func(opts)
        assert result == opts, f"Paths were modified when they shouldn't be: {result}"
    finally:
        os.environ.pop("VCToolsInstallDir", None)


# [pr_diff] fail_to_pass
def test_no_filter_without_env_var():
    """Paths preserved when VCToolsInstallDir is not set."""
    func = _exec_filter_func("20250300")
    os.environ.pop("VCToolsInstallDir", None)
    opts = [
        "-DSOME_DEFINE",
        r"-IC:\some\msvc\path\include",
        "-I/some/other/path",
    ]
    result = func(opts)
    assert len(result) == len(opts), (
        f"Expected {len(opts)} items (no filtering without env var), got {len(result)}"
    )


# [pr_diff] fail_to_pass
def test_filter_empty_opts():
    """Filtering an empty pp_opts list returns empty list."""
    func = _exec_filter_func("20250300")
    os.environ["VCToolsInstallDir"] = r"C:\VS\VC\Tools\MSVC\14.38"
    try:
        result = func([])
        assert result == [], f"Expected empty list, got: {result}"
    finally:
        os.environ.pop("VCToolsInstallDir", None)


# [pr_diff] fail_to_pass
def test_filter_applied_in_sycl_cflags():
    """sycl_cflags construction wraps pp_opts through the filter function."""
    # AST-only because: sycl_cflags is constructed inside win_wrap_ninja_compile
    # which requires a full Windows build environment with MSVC + oneAPI to call
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
