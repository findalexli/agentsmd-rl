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
import subprocess
import textwrap
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
    """sycl_cflags construction filters MSVC include dirs when oneAPI >= 2025.3.

    Tests integration by extracting the sycl_cflags computation block from
    win_wrap_ninja_compile and executing it with controlled inputs.
    On unpatched code, win_filter_msvc_include_dirs doesn't exist so the
    subprocess fails.  On patched code, MSVC paths are filtered out of the
    resulting sycl_cflags regardless of how the integration was implemented.
    """
    vc_tools_dir = r"C:\VS\VC\Tools\MSVC\14.38"
    msvc_include = rf"-I{vc_tools_dir}\include"
    pp_opts_input = ["-DFOO", msvc_include, "-I/other"]

    script = textwrap.dedent(f"""\
        import os, ast, textwrap, json
        from pathlib import Path

        source = Path({str(TARGET)!r}).read_text()
        tree = ast.parse(source)

        os.environ['VCToolsInstallDir'] = {vc_tools_dir!r}

        ns = {{'os': os}}
        exec("def _get_icpx_version(): return '20250300'", ns)

        # Extract win_filter_msvc_include_dirs
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'win_filter_msvc_include_dirs':
                func_src = ast.get_source_segment(source, node)
                exec(textwrap.dedent(func_src), ns)
                found = True
                break
        if not found:
            print(json.dumps({{'error': 'win_filter_msvc_include_dirs not found'}}))
            raise SystemExit(1)

        # Find win_wrap_ninja_compile
        wrap_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'win_wrap_ninja_compile':
                wrap_func = node
                break
        if wrap_func is None:
            print(json.dumps({{'error': 'win_wrap_ninja_compile not found'}}))
            raise SystemExit(1)

        # Find the 'if with_sycl:' block inside win_wrap_ninja_compile
        sycl_block = None
        for child in ast.walk(wrap_func):
            if isinstance(child, ast.If):
                if isinstance(child.test, ast.Name) and child.test.id == 'with_sycl':
                    sycl_block = child
                    break
        if sycl_block is None:
            print(json.dumps({{'error': 'if with_sycl block not found'}}))
            raise SystemExit(1)

        # Extract statements up to and including the first sycl_cflags assignment
        stmts = []
        for stmt in sycl_block.body:
            src = ast.get_source_segment(source, stmt)
            if src:
                stmts.append(textwrap.dedent(src))
            if isinstance(stmt, ast.Assign):
                if any(isinstance(t, ast.Name) and t.id == 'sycl_cflags' for t in stmt.targets):
                    break

        # Provide mocked variables
        ns['common_cflags'] = ['-O2']
        ns['pp_opts'] = {pp_opts_input!r}
        ns['_COMMON_SYCL_FLAGS'] = ['-fsycl']

        # Execute the extracted statements
        for s in stmts:
            exec(s, ns)

        sycl_cflags = ns.get('sycl_cflags')
        if sycl_cflags is None:
            print(json.dumps({{'error': 'sycl_cflags not assigned'}}))
            raise SystemExit(1)

        print(json.dumps(sycl_cflags))
    """)

    script_path = Path(REPO) / "_eval_integration.py"
    script_path.write_text(script)
    try:
        r = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=30,
        )
    finally:
        script_path.unlink(missing_ok=True)

    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    result = json.loads(r.stdout.strip())

    # Verify sycl_cflags contains expected non-MSVC items
    assert "-O2" in result, f"common_cflags not in sycl_cflags: {result}"
    assert "-fsycl" in result, f"_COMMON_SYCL_FLAGS not in sycl_cflags: {result}"
    assert "-DFOO" in result, f"non-MSVC define should be preserved: {result}"
    assert "-I/other" in result, f"non-MSVC include should be preserved: {result}"

    # Key assertion: MSVC paths must be filtered out
    for item in result:
        assert vc_tools_dir not in item, (
            f"MSVC path not filtered from sycl_cflags: {item}"
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


# [repo_tests] pass_to_pass - CI/CD gate
def test_repo_pyflakes():
    """Target file passes pyflakes static analysis (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "pyflakes", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pyflakes", str(TARGET)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"pyflakes failed:\n{r.stdout}\n{r.stderr}"
    assert r.stdout == "", f"pyflakes found issues:\n{r.stdout}"


# [repo_tests] pass_to_pass - CI/CD gate
def test_repo_py_compile():
    """Target file compiles to bytecode without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(TARGET)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"

# [repo_tests] pass_to_pass - CI/CD gate (flake8)
def test_repo_flake8():
    """Target file passes flake8 linting per repo config (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "flake8", str(TARGET)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"flake8 failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - CI/CD gate (ruff)
def test_repo_ruff():
    """Target file passes ruff linting per repo config (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", str(TARGET)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Additional CI gate added during p2p enrichment
# Verifies AST integrity and that key functions exist in the module
def test_repo_module_ast_integrity():
    """Target file has valid AST with expected top-level constructs (pass_to_pass)."""
    source = TARGET.read_text()
    tree = ast.parse(source)
    # Check for expected function definitions
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "win_cuda_flags" in func_names, "win_cuda_flags function missing from AST"
    assert "win_hip_flags" in func_names, "win_hip_flags function missing from AST"
    assert "win_wrap_ninja_compile" in func_names, "win_wrap_ninja_compile function missing from AST"




# [repo_tests] pass_to_pass - Security scan
# Added during p2p enrichment: bandit security check for common Python security issues
def test_repo_bandit():
    """Target file passes bandit security scan (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "bandit", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "bandit", "-f", "json", "-o", "/dev/null", str(TARGET)],
        capture_output=True, text=True, timeout=60,
    )
    # Bandit exits 0 even if it finds issues when output is redirected
    # Check for high-severity issues in stderr/stdout
    if r.returncode != 0:
        # Only fail for high/medium severity, not low
        assert "HIGH" not in r.stdout and "HIGH" not in r.stderr, f"Bandit found HIGH severity issues:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Code quality check
# Added during p2p enrichment: pylint errors-only check for code correctness
def test_repo_pylint_errors_only():
    """Target file has no pylint errors (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pylint", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pylint", str(TARGET), "--errors-only", "--disable=E0401,E0601,E0606"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Filter out import errors (E0401) and used-before-assignment errors (E0601, E0606)
    # which are false positives due to torch not being built
    error_lines = [line for line in r.stdout.splitlines() + r.stderr.splitlines()
                   if ": error" in line and "E0401" not in line and "E0601" not in line and "E0606" not in line]
    newline = chr(10)
    assert len(error_lines) == 0, f"Pylint found errors:\n{newline.join(error_lines)}"


# [repo_tests] pass_to_pass - AST validation for key constants
# Added during p2p enrichment: verify key constants are defined with proper types
def test_repo_constants_defined():
    """Key module constants are properly defined (pass_to_pass)."""
    source = TARGET.read_text()
    tree = ast.parse(source)

    # Check for expected constant definitions
    expected_constants = [
        "_COMMON_SYCL_FLAGS",
        "IS_WINDOWS",
        "IS_LINUX",
        "IS_MACOS",
    ]

    assign_names = {node.targets[0].id for node in ast.walk(tree)
                    if isinstance(node, ast.Assign)
                    and isinstance(node.targets[0], ast.Name)}

    for const in expected_constants:
        assert const in assign_names, f"Expected constant '{const}' not found in module"


# [repo_tests] pass_to_pass - API surface check
# Added during p2p enrichment: verify public API exports are present
def test_repo_public_api_exports():
    """Public API exports are defined (pass_to_pass)."""
    source = TARGET.read_text()
    tree = ast.parse(source)

    # Check __all__ exports exist
    all_exports = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        all_exports = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                    break

    assert all_exports is not None, "__all__ not found in module"
    expected_exports = [
        "get_default_build_root",
        "CppExtension",
        "CUDAExtension",
        "SyclExtension",
        "include_paths",
        "library_paths",
        "load",
        "load_inline",
    ]
    for export in expected_exports:
        assert export in all_exports, f"Expected export '{export}' missing from __all__"


# [repo_tests] pass_to_pass - Extension function definitions check
# Added during p2p enrichment: verify key extension functions are defined
def test_repo_extension_functions_defined():
    """Key extension functions are defined in the module (pass_to_pass)."""
    source = TARGET.read_text()
    tree = ast.parse(source)

    # Check for expected function definitions (CppExtension, CUDAExtension etc are functions)
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    expected_funcs = [
        "CppExtension",
        "CUDAExtension",
        "SyclExtension",
        "load",
        "load_inline",
    ]

    for func in expected_funcs:
        assert func in func_names, f"Expected function '{func}' not found in module"
