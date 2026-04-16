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
        r = subprocess.run(
            ["g++", "-std=c++17", "-o", str(test_bin), str(test_cpp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        if r.returncode != 0:
            return r.returncode, "", r.stderr
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

    match = re.search(
        r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+torch_from_blob\s*\(([^;]+)\)\s*;',
        src,
        re.DOTALL,
    )
    assert match, "No torch_from_blob declaration found in shim.h"
    params = match.group(1).strip()

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
    ops_src = OPS_H.read_text()
    lines = ops_src.split('\n')

    # Find the from_blob overload that has a deleter parameter
    deleter_from_blob_line = None
    for i, line in enumerate(lines):
        if re.search(r'\bfrom_blob\s*\(', line):
            block = '\n'.join(lines[i:i + 15])
            if re.search(r'\bdeleter\b', block):
                deleter_from_blob_line = i
                break

    assert deleter_from_blob_line is not None, (
        "No from_blob overload with deleter parameter found in ops.h"
    )

    # Check whether a template declaration exists above the function
    is_template = False
    for j in range(deleter_from_blob_line - 1,
                    max(deleter_from_blob_line - 5, -1), -1):
        if 'template' in lines[j]:
            is_template = True
            break

    # Extract the deleter parameter type name
    deleter_type = None
    for j in range(deleter_from_blob_line,
                    min(deleter_from_blob_line + 15, len(lines))):
        m = re.search(r'(?:const\s+)?(\w+)\s*(?:[&*]+)?\s+deleter\b', lines[j])
        if m:
            deleter_type = m.group(1)
            break

    assert deleter_type is not None, (
        "Could not determine deleter parameter type in ops.h from_blob"
    )

    # Build a minimal C++ test: create a function with the extracted template
    # (if any) and deleter type, then call it with a capturing lambda.
    # Base commit: deleter type is a fixed function pointer typedef -> lambda
    #   cannot convert -> compilation fails.
    # Fixed commit: deleter type is a template parameter -> lambda matches
    #   -> compilation succeeds.
    template_line = f'template <class {deleter_type}>' if is_template else ''

    cpp_code = f"""\
#include <type_traits>
#include <cstdio>

typedef void (*DeleterFnPtr)(void*);

{template_line}
int test_from_blob({deleter_type} deleter) {{
    deleter(nullptr);
    return 0;
}}

int main() {{
    int captured = 42;
    auto lambda = [&captured](void*) {{ captured = 0; }};
    test_from_blob(lambda);
    if (captured == 0) {{
        printf("PASS\\n");
        return 0;
    }}
    printf("FAIL\\n");
    return 1;
}}
"""
    rc, stdout, stderr = _compile_and_run(cpp_code)
    assert rc == 0, (
        f"Compilation/execution failed — ops.h from_blob cannot accept "
        f"capturing lambda as deleter:\n{stderr}"
    )
    assert "PASS" in stdout


def test_shim_cpp_context_forwarded():
    """shim_common.cpp forwards context pointer through wrapping lambda."""
    src = SHIM_CPP.read_text()

    # Extract the torch_from_blob function definition parameter list
    match = re.search(
        r'(?:AOTI_TORCH_EXPORT\s+)?AOTITorchError\s+torch_from_blob\s*\(([^{]+)\)\s*\{',
        src,
        re.DOTALL,
    )
    assert match, "No torch_from_blob definition found in shim_common.cpp"
    params = match.group(1).strip()

    # Detect a two-arg function pointer: void (*name)(... void* ..., void* ...)
    fp_match = re.search(
        r'void\s*\(\s*\*\s*(\w+)\s*\)\s*\([^)]*void\s*\*[^)]*,\s*void\s*\*',
        params,
    )

    if fp_match:
        callback_name = fp_match.group(1)
        # The context void* parameter follows the function pointer
        remaining = params[fp_match.end():]
        ctx_match = re.search(r'void\s*\*\s*(\w+)', remaining)
        ctx_name = ctx_match.group(1) if ctx_match else None
        # First void* parameter is the data pointer
        data_match = re.search(r'void\s*\*\s*(\w+)', params)
        data_name = data_match.group(1) if data_match else 'data'

        mock_body = (
            f"    if ({callback_name} != nullptr)\n"
            f"        {callback_name}({data_name}, {ctx_name});\n"
            f"    return 0;"
        )
    else:
        mock_body = "    return 0;"

    cpp_code = f"""\
#define AOTI_TORCH_EXPORT
typedef int AOTITorchError;
typedef void* AtenTensorHandle;
#include <cstdint>
#include <cstdio>

AOTITorchError torch_from_blob({params}) {{
{mock_body}
}}

static void context_deleter(void* data, void* ctx) {{
    *(int*)ctx = 99;
}}

int main() {{
    int ctx_val = 0;
    AtenTensorHandle handle = nullptr;
    AOTITorchError err = torch_from_blob(
        nullptr, 1, nullptr, nullptr, 0, 0, 0, 0,
        &handle, 0, nullptr, 0,
        context_deleter, &ctx_val);
    if (err != 0) return 1;
    if (ctx_val == 99) {{
        printf("PASS\\n");
        return 0;
    }}
    printf("FAIL: context not forwarded (ctx_val=%d)\\n", ctx_val);
    return 1;
}}
"""
    rc, stdout, stderr = _compile_and_run(cpp_code)
    assert rc == 0, (
        f"Compilation/execution failed — shim_common.cpp torch_from_blob "
        f"definition doesn't support two-arg deleter + context:\n{stderr}"
    )
    assert "PASS" in stdout, (
        f"Context forwarding verification failed — the two-arg callback "
        f"was not invoked with the context pointer:\n{stdout}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — backward compatibility + anti-stub (origin: static)
# ---------------------------------------------------------------------------

def test_repo_git_clean():
    """Repo is at expected base commit with no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
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
        assert "#include" in content or "#pragma" in content or "//" in content, (
            f"{path} appears to be corrupted (no expected C++ markers)"
        )


def test_repo_header_structure():
    """C++ headers have valid include guards/pragma once (pass_to_pass)."""
    for path in [SHIM_H, OPS_H]:
        content = path.read_text()
        has_guard = re.search(r'#ifndef\s+\w+', content) is not None
        has_pragma = "#pragma once" in content
        assert has_guard or has_pragma, (
            f"{path.name} missing include guards or #pragma once"
        )


def test_repo_code_formatting():
    """Modified files follow basic code formatting rules (pass_to_pass)."""
    for path in [SHIM_H, OPS_H, SHIM_CPP]:
        src = path.read_text()
        lines = src.split('\n')
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                assert False, f"{path.name}:{i} has trailing whitespace"
        if '\t' in src:
            assert False, f"{path.name} contains tab characters, should use spaces"
        if src and not src.endswith('\n'):
            assert False, f"{path.name} does not end with a newline"


def test_repo_file_structure():
    """Source files have valid internal structure (pass_to_pass)."""
    shim_src = SHIM_H.read_text()
    assert '#ifdef __cplusplus' in shim_src, "shim.h missing __cplusplus guard"
    assert 'extern "C"' in shim_src, "shim.h missing extern C declaration"

    ops_src = OPS_H.read_text()
    has_ns = 'namespace' in ops_src or 'HIDDEN_NAMESPACE_' in ops_src
    assert has_ns, "ops.h missing namespace declarations"

    for path, name in [(OPS_H, "ops.h"), (SHIM_CPP, "shim_common.cpp")]:
        src = path.read_text()
        open_braces = src.count('{')
        close_braces = src.count('}')
        assert open_braces == close_braces, (
            f"{name} has mismatched braces: {open_braces} open, {close_braces} close"
        )

    shim_cpp_src = SHIM_CPP.read_text()
    ifdefs = len(re.findall(r'#if(?:def|ndef)?\b', shim_cpp_src))
    endifs = len(re.findall(r'#endif\b', shim_cpp_src))
    assert ifdefs == endifs, (
        f"shim_common.cpp has mismatched preprocessor: {ifdefs} if, {endifs} endif"
    )


def test_no_deleter_overload_preserved():
    """The no-deleter from_blob overload still exists for backward compatibility."""
    src = OPS_H.read_text()
    from_blob_defs = re.findall(
        r'(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(', src
    )
    assert len(from_blob_defs) >= 2, (
        f"Expected >= 2 from_blob overloads, found {len(from_blob_defs)}"
    )
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
# ---------------------------------------------------------------------------

def test_repo_git_history():
    """Repo has expected git history and structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "git log returned empty"


def test_repo_ci_scripts_syntax():
    """CI scripts have valid Python syntax (pass_to_pass)."""
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
            continue
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
