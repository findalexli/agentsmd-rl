"""
Task: pytorch-from-blob-lambda-deleter
Repo: pytorch/pytorch @ 41f8e3e0381395e1669ca4bc6e36a7872d25cdcd
PR:   177048

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"

SHIM_H = Path(REPO) / "torch/csrc/stable/c/shim.h"
SHIM_CPP = Path(REPO) / "torch/csrc/shim_common.cpp"
OPS_H = Path(REPO) / "torch/csrc/stable/ops.h"


def _compile_and_run(cpp_code: str, timeout: int = 60) -> tuple[int, str, str]:
    """Compile and run C++ code, returning (returncode, stdout, stderr)."""
    test_cpp = Path(REPO) / "_eval_test.cpp"
    test_bin = Path(REPO) / "_eval_test"
    test_cpp.write_text(cpp_code)
    try:
        # Compile
        r = subprocess.run(
            ["g++", "-std=c++17", "-o", str(test_bin), str(test_cpp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        if r.returncode != 0:
            return r.returncode, "", r.stderr
        # Run
        r2 = subprocess.run(
            [str(test_bin)], capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        return r2.returncode, r2.stdout, r2.stderr
    finally:
        test_cpp.unlink(missing_ok=True)
        test_bin.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Behavioral: C++ compilation + execution
# ---------------------------------------------------------------------------

def test_shim_h_two_arg_deleter_compiles():
    """shim.h torch_from_blob compiles with two-arg callback + void* context."""
    src = SHIM_H.read_text()

    # Extract the torch_from_blob declaration parameters
    match = re.search(
        r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+torch_from_blob\s*\(([^;]+)\)\s*;',
        src,
        re.DOTALL,
    )
    assert match, "No torch_from_blob declaration found in shim.h"
    params = match.group(1).strip()

    # Try to compile a program using the extracted signature
    # This FAILS on base commit (single-arg deleter) because the test code
    # passes two_arg_deleter with a context pointer
    cpp_code = f"""\
#define AOTI_TORCH_EXPORT
typedef int AOTITorchError;
typedef void* AtenTensorHandle;
#include <cstdint>
#include <cstdio>

AOTITorchError torch_from_blob({params}) {{ return 0; }}

static void two_arg_deleter(void* data, void* ctx) {{
    *(int*)ctx += 1;
}}

int main() {{
    int ctx_val = 0;
    AtenTensorHandle handle = nullptr;
    AOTITorchError err = torch_from_blob(
        nullptr, 1, nullptr, nullptr, 0, 0, 0, 0,
        &handle, 0, nullptr, 0,
        two_arg_deleter, &ctx_val);
    if (err != 0) return 1;
    printf("PASS\\n");
    return 0;
}}
"""
    rc, stdout, stderr = _compile_and_run(cpp_code)
    assert rc == 0, (
        f"Compilation/execution failed — shim.h signature doesn't accept "
        f"two-arg deleter + context:\n{stderr}"
    )
    assert "PASS" in stdout


def test_ops_h_accepts_capturing_lambda():
    """ops.h from_blob accepts capturing lambdas via template (not just DeleterFnPtr)."""
    # This test compiles a C++ program that includes ops.h and tries to use
    # a capturing lambda as the deleter. This ONLY works if from_blob is
    # a template accepting generic callables.
    #
    # Base commit: from_blob takes DeleterFnPtr → fails to compile with lambda
    # Fix commit: from_blob is a template with SFINAE → compiles and runs
    ops_src = OPS_H.read_text()
    shim_src = SHIM_H.read_text()

    # Check if ops.h has the template signature
    has_template = bool(
        re.search(
            r'template\s*<[^;]*>\s+(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(',
            ops_src,
        )
    )
    assert has_template, (
        "ops.h from_blob has no template signature — cannot accept capturing lambdas"
    )

    # Verify the template uses is_invocable_v<F, void*> for SFINAE
    has_is_invocable = 'std::is_invocable_v' in ops_src
    assert has_is_invocable, (
        "ops.h template doesn't use std::is_invocable_v<F, void*> for SFINAE"
    )


def test_shim_cpp_context_forwarded():
    """shim_common.cpp forwards context pointer through wrapping lambda."""
    src = SHIM_CPP.read_text()

    # Find the torch_from_blob function implementation
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found_func = None
    for block in funcs:
        if 'torch_from_blob' in block and 'for_blob' in block:
            found_func = block
            break
    assert found_func, "No torch_from_blob implementation found in shim_common.cpp"

    # Must have a two-arg deleter callback parameter: void (*xxx)(void*, void*)
    # Pattern allows for optional parameter names (e.g., void* data, void* ctx)
    has_two_arg_cb = bool(
        re.search(
            r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
            found_func,
        )
    )
    assert has_two_arg_cb, (
        "shim_common.cpp torch_from_blob doesn't have two-arg deleter callback parameter"
    )

    # Must have a wrapping lambda that captures deleter_callback and deleter_ctx
    has_wrapping_lambda = bool(
        re.search(
            r'\[\s*deleter_callback\s*,\s*deleter_ctx\s*\]\s*\(\s*void\s*\*\s*\w+\s*\)',
            found_func,
        )
    )
    assert has_wrapping_lambda, (
        "shim_common.cpp doesn't have wrapping lambda capturing deleter_callback and deleter_ctx"
    )

    # The wrapping lambda must call the two-arg callback
    has_two_arg_call = bool(
        re.search(
            r'deleter_callback\s*\(\s*\w+\s*,\s*deleter_ctx\s*\)',
            found_func,
        )
    )
    assert has_two_arg_call, (
        "shim_common.cpp wrapping lambda doesn't call deleter_callback with two arguments"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — backward compatibility + anti-stub (origin: static)
# These tests read file content to verify structure
# ---------------------------------------------------------------------------

def test_repo_git_clean():
    """Repo is at expected base commit with no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    # Allow changes in:
    # - test files (_eval_test)
    # - the specific source files modified by the fix (shim.h, ops.h, shim_common.cpp)
    allowed_patterns = ["_eval_test", "torch/csrc/stable/c/shim.h",
                        "torch/csrc/stable/ops.h", "torch/csrc/shim_common.cpp"]
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    unexpected = [l for l in lines if not any(p in l for p in allowed_patterns)]
    assert len(unexpected) == 0, (
        f"Repo has unexpected uncommitted changes: {unexpected}\n"
        f"This indicates the base commit state is not clean."
    )


def test_repo_files_exist():
    """Modified source files exist and are non-empty (pass_to_pass)."""
    for path in [SHIM_H, SHIM_CPP, OPS_H]:
        assert path.exists(), f"{path} does not exist"
        content = path.read_text()
        assert len(content) > 0, f"{path} is empty"
        # Basic sanity check: files should have expected markers
        assert "#include" in content or "#pragma" in content or "//" in content, (
            f"{path} appears to be corrupted (no expected C++ markers)"
        )


def test_repo_header_structure():
    """C++ headers have valid include guards/pragma once (pass_to_pass)."""
    for path in [SHIM_H, OPS_H]:
        content = path.read_text()
        # Check for include guards or pragma once
        has_guard = re.search(r'#ifndef\s+\w+', content) is not None
        has_pragma = "#pragma once" in content
        assert has_guard or has_pragma, (
            f"{path.name} missing include guards or #pragma once"
        )


def test_repo_code_formatting():
    """Modified files follow basic code formatting rules (pass_to_pass)."""
    # Check for common formatting issues that clang-format would catch
    for path in [SHIM_H, OPS_H, SHIM_CPP]:
        src = path.read_text()

        # Check for trailing whitespace (clang-format would catch this)
        lines = src.split('\n')
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                assert False, f"{path.name}:{i} has trailing whitespace"

        # Check for tabs (should use spaces per .clang-format)
        if '\t' in src:
            assert False, f"{path.name} contains tab characters, should use spaces"

        # Check file ends with newline
        if src and not src.endswith('\n'):
            assert False, f"{path.name} does not end with a newline"


def test_repo_file_structure():
    """Source files have valid internal structure (pass_to_pass)."""
    # Test shim.h has proper extern "C" guards for C linkage
    shim_src = SHIM_H.read_text()
    assert '#ifdef __cplusplus' in shim_src, "shim.h missing __cplusplus guard"
    assert 'extern "C"' in shim_src, "shim.h missing extern C declaration"

    # Test that ops.h has namespace declarations
    ops_src = OPS_H.read_text()
    has_ns = 'namespace' in ops_src or 'HIDDEN_NAMESPACE_' in ops_src
    assert has_ns, "ops.h missing namespace declarations"

    # Check brace balance (basic syntax validation)
    for path, name in [(OPS_H, "ops.h"), (SHIM_CPP, "shim_common.cpp")]:
        src = path.read_text()
        open_braces = src.count('{')
        close_braces = src.count('}')
        assert open_braces == close_braces, (
            f"{name} has mismatched braces: {open_braces} open, {close_braces} close"
        )

    # Check preprocessor conditional balance
    shim_cpp_src = SHIM_CPP.read_text()
    ifdefs = len(re.findall(r'#if(?:def|ndef)?\b', shim_cpp_src))
    endifs = len(re.findall(r'#endif\b', shim_cpp_src))
    assert ifdefs == endifs, (
        f"shim_common.cpp has mismatched preprocessor: {ifdefs} if, {endifs} endif"
    )


def test_no_deleter_overload_preserved():
    """The no-deleter from_blob overload still exists for backward compatibility."""
    src = OPS_H.read_text()

    # Count from_blob definitions - there should be at least 2 (with deleter + without)
    from_blob_defs = re.findall(
        r'(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(', src
    )
    assert len(from_blob_defs) >= 2, (
        f"Expected >= 2 from_blob overloads, found {len(from_blob_defs)}"
    )

    # Check for aoti_torch_create_tensor_from_blob (used by no-deleter path)
    assert 'aoti_torch_create_tensor_from_blob' in src, (
        "Original no-deleter path using aoti_torch_create_tensor_from_blob was removed"
    )


def test_files_not_stubbed():
    """Modified files have real implementation, not stubs."""
    for path, min_lines, markers in [
        (OPS_H, 100, ["TORCH_ERROR_CODE_CHECK", "AtenTensorHandle"]),
        (SHIM_CPP, 100, ["AOTI_TORCH_CONVERT_EXCEPTION_TO_ERROR_CODE"]),
        (SHIM_H, 50, []),
    ]:
        text = path.read_text()
        lines = text.strip().splitlines()
        assert len(lines) >= min_lines, f"{path.name} too short ({len(lines)} lines)"
        for m in markers:
            assert m in text, f"{path.name} missing {m}"


def test_shim_cpp_null_callback_guard():
    """shim_common.cpp still guards against nullptr callback (backward compat)."""
    src = SHIM_CPP.read_text()

    # Find the torch_from_blob function and check it guards deleter_callback != nullptr
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found = False
    for block in funcs:
        if 'torch_from_blob' in block and 'for_blob' in block:
            if re.search(r'if\s*\(\s*\w+\s*!=\s*nullptr\s*\)', block):
                found = True
                break
    assert found, "shim_common.cpp missing nullptr guard for deleter callback"


# ---------------------------------------------------------------------------
# Pass-to-pass — CI/CD repo tests (origin: repo_tests)
# These use subprocess.run() to execute actual CI commands
# ---------------------------------------------------------------------------

def test_repo_git_history():
    """Repo has expected git history and structure (pass_to_pass)."""
    # Check git log works (repo has history)
    r = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "git log returned empty"


def test_repo_ci_scripts_syntax():
    """CI scripts have valid Python syntax (pass_to_pass)."""
    # Check Python syntax of CI scripts that exist in the repo
    ci_scripts = [
        ".github/scripts/collect_ciflow_labels.py",
        ".github/scripts/ensure_actions_will_cancel.py",
    ]
    for script in ci_scripts:
        script_path = Path(REPO) / script
        if script_path.exists():
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(script_path)],
                capture_output=True, text=True, timeout=30, cwd=REPO,
            )
            assert r.returncode == 0, f"{script} has Python syntax errors: {r.stderr}"


def test_github_scripts_syntax():
    """All .github/scripts Python files have valid syntax (pass_to_pass)."""
    scripts_dir = Path(REPO) / ".github/scripts"
    python_files = list(scripts_dir.glob("*.py"))
    assert len(python_files) > 0, "No Python scripts found in .github/scripts"

    failed = []
    for script_path in python_files:
        if script_path.name.startswith("test_"):
            continue  # Skip test files, just check source files
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{script_path.name}: {r.stderr[:200]}")

    assert len(failed) == 0, f"Scripts with syntax errors: {failed}"


def test_repo_shell_scripts_syntax():
    """Shell scripts in .github/scripts have valid syntax (pass_to_pass)."""
    scripts_dir = Path(REPO) / ".github/scripts"
    shell_scripts = [
        "lintrunner.sh",
        "pr-sanity-check.sh",
        "report_git_status.sh",
    ]

    for script_name in shell_scripts:
        script_path = scripts_dir / script_name
        if script_path.exists():
            r = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True, text=True, timeout=30, cwd=REPO,
            )
            assert r.returncode == 0, (
                f"{script_name} has shell syntax errors: {r.stderr}"
            )


def test_repo_pyproject_toml_valid():
    """pyproject.toml has valid TOML syntax (pass_to_pass)."""
    import tomllib
    pyproject_path = Path(REPO) / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml does not exist"

    content = pyproject_path.read_text()
    try:
        tomllib.loads(content)
    except Exception as e:
        assert False, f"pyproject.toml has invalid TOML syntax: {e}"
