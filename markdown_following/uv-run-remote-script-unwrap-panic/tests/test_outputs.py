"""
Task: uv-run-remote-script-unwrap-panic
Repo: astral-sh/uv @ 867e535f2a5f7f2b1f22a0ccc52fc6da5b01ac3c
PR:   18707

Test suite verifying that the unsafe `.unwrap()` on downloaded_script
is eliminated and the downloaded file is no longer threaded separately
through the call chain.  Tests check for the ABSENCE of the old broken
patterns rather than the PRESENCE of a specific fix, so any correct
restructuring (NamedTempFile, PathBuf, etc.) will pass.
"""

import re
import subprocess

import pytest
from pathlib import Path

REPO = "/repo"
RUN_RS = Path(REPO) / "crates/uv/src/commands/project/run.rs"
LIB_RS = Path(REPO) / "crates/uv/src/lib.rs"


# ---------------------------------------------------------------------------
# Helpers for structural checks
# ---------------------------------------------------------------------------

def _extract_function_body(source, func_name):
    lines = source.split("\n")
    in_func = False
    brace_depth = 0
    body_started = False
    func_lines = []
    for line in lines:
        if not in_func and re.search(rf"\bfn\s+{func_name}\b", line):
            in_func = True
        if in_func:
            func_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth > 0:
                body_started = True
            if body_started and brace_depth <= 0:
                break
    return "\n".join(func_lines)


def _extract_fn_signature(source, func_name):
    lines = source.split("\n")
    in_sig = False
    sig_lines = []
    for line in lines:
        if not in_sig and re.search(rf"\bfn\s+{func_name}\b", line):
            in_sig = True
        if in_sig:
            sig_lines.append(line)
            if "{" in line:
                break
    return " ".join(sig_lines)


def _extract_enum_body(source, enum_name):
    lines = source.split("\n")
    in_enum = False
    brace_depth = 0
    enum_lines = []
    for line in lines:
        if not in_enum and re.search(rf"\benum\s+{enum_name}\b", line):
            in_enum = True
        if in_enum:
            enum_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(enum_lines) > 1:
                break
    return "\n".join(enum_lines)


def _extract_match_arm(body, variant_name):
    lines = body.split("\n")
    arm_lines = []
    in_arm = False
    brace_depth = 0
    for line in lines:
        if variant_name in line and not line.strip().startswith("//"):
            in_arm = True
            brace_depth = 0
        if in_arm:
            arm_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(arm_lines) > 1:
                break
    return "\n".join(arm_lines)


# ===================================================================
# pass_to_pass tests
# ===================================================================

# [repo_tests] pass_to_pass
def test_repo_cargo_check():
    """Repo Rust code compiles with cargo check."""
    try:
        r = subprocess.run(
            ["cargo", "check", "-p", "uv"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"
    except subprocess.TimeoutExpired:
        pytest.skip("cargo check timed out")


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Repo Rust code is formatted correctly."""
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_as_command_not_stub():
    """as_command has a real implementation with meaningful logic."""
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"
    meaningful = [
        line for line in body.split("\n")
        if line.strip()
        and not line.strip().startswith("//")
        and line.strip() not in ("{", "}", "}")
    ]
    assert len(meaningful) >= 8, (
        f"as_command has only {len(meaningful)} meaningful lines"
    )


# [static] pass_to_pass
def test_python_remote_variant_exists():
    """PythonRemote variant still exists in RunCommand enum."""
    src = RUN_RS.read_text()
    body = _extract_enum_body(src, "RunCommand")
    assert body, "RunCommand enum not found"
    assert "PythonRemote" in body, "PythonRemote variant missing"


# [static] pass_to_pass
def test_as_command_handles_all_variants():
    """as_command still handles PythonRemote alongside other variants."""
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"
    for variant in ["Python(", "PythonRemote"]:
        assert variant in body, f"as_command missing {variant}"


# ===================================================================
# fail_to_pass tests
# ===================================================================

# [pr_diff] fail_to_pass
def test_run_fn_no_downloaded_script_param():
    """run() in run.rs must not accept downloaded_script as a parameter.

    On the base commit, run() accepts downloaded_script as a separate
    Option parameter.  The fix should remove it from the signature.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Crate does not compile:\n{r.stderr[:500]}"

    src = RUN_RS.read_text()
    sig = _extract_fn_signature(src, "run")
    assert sig, "run() function not found in run.rs"
    assert "downloaded_script" not in sig, (
        "run() still takes downloaded_script parameter"
    )


# [pr_diff] fail_to_pass
def test_lib_no_downloaded_script_threading():
    """run_project() in lib.rs must not thread downloaded_script.

    On the base commit, run_project() accepts downloaded_script as
    a separate Option parameter and passes it through.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Crate does not compile:\n{r.stderr[:500]}"

    src = LIB_RS.read_text()
    sig = _extract_fn_signature(src, "run_project")
    assert sig, "run_project not found in lib.rs"
    assert "downloaded_script" not in sig, (
        "run_project() still takes downloaded_script"
    )


# [pr_diff] fail_to_pass
def test_python_remote_not_url_only():
    """PythonRemote variant must not hold only a DisplaySafeUrl.

    On the base commit, PythonRemote is defined as
    PythonRemote(DisplaySafeUrl, Vec<OsString>), storing only a URL.
    The fix should change this so the variant is no longer URL-only.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Crate does not compile:\n{r.stderr[:500]}"

    src = RUN_RS.read_text()
    body = _extract_enum_body(src, "RunCommand")
    assert body, "RunCommand enum not found"

    # Find PythonRemote variant definition lines (skip comments)
    python_remote_lines = [
        l for l in body.split("\n")
        if "PythonRemote" in l and not l.strip().startswith("//")
    ]
    assert python_remote_lines, "PythonRemote variant not found"

    variant_text = " ".join(python_remote_lines)
    assert "DisplaySafeUrl" not in variant_text, (
        "PythonRemote still holds a DisplaySafeUrl (URL-only) — "
        "it should be associated with the downloaded file"
    )


# [pr_diff] fail_to_pass
def test_as_command_no_option_downloaded_script():
    """as_command() must not accept a separate downloaded_script parameter.

    On the base commit, as_command takes
    downloaded_script: Option<&tempfile::NamedTempFile> as a third
    parameter.  The fix should remove this separate parameter.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Crate does not compile:\n{r.stderr[:500]}"

    src = RUN_RS.read_text()
    sig = _extract_fn_signature(src, "as_command")
    assert sig, "as_command function not found"
    assert "downloaded_script" not in sig, (
        "as_command still takes downloaded_script as a parameter"
    )


# [pr_diff] fail_to_pass
def test_no_unwrap_in_python_remote_arm():
    """The PythonRemote arm of as_command() must not call .unwrap().

    On the base commit, the PythonRemote arm calls
    downloaded_script.unwrap().path() which can panic at runtime.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Crate does not compile:\n{r.stderr[:500]}"

    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"
    arm = _extract_match_arm(body, "PythonRemote")

    if not arm:
        assert ".unwrap()" not in body or "downloaded_script" not in body, (
            "PythonRemote arm not found but downloaded_script.unwrap() present"
        )
        return

    assert ".unwrap()" not in arm, (
        f"PythonRemote arm uses .unwrap(): {arm}"
    )


# [agent_config] fail_to_pass
def test_no_panic_apis_in_remote_handling():
    """No .unwrap(), panic!(), or unreachable!() in PythonRemote arm.

    The repository CLAUDE.md states: AVOID using panic!, unreachable!,
    .unwrap(), unsafe code, and clippy rule ignores.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Crate does not compile:\n{r.stderr[:500]}"

    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"
    arm = _extract_match_arm(body, "PythonRemote")

    if not arm:
        assert "downloaded_script" not in body or ".unwrap()" not in body, (
            "PythonRemote arm not found but downloaded_script.unwrap() present"
        )
        return

    assert ".unwrap()" not in arm, (
        f"PythonRemote arm uses .unwrap(): {arm}"
    )
    assert "panic!" not in arm, (
        f"PythonRemote arm uses panic!(): {arm}"
    )
    assert "unreachable!" not in arm, (
        f"PythonRemote arm uses unreachable!(): {arm}"
    )
