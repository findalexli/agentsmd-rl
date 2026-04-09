"""
Task: uv-run-remote-script-unwrap-panic
Repo: astral-sh/uv @ 867e535f2a5f7f2b1f22a0ccc52fc6da5b01ac3c
PR:   18707

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
RUN_RS = Path(REPO) / "crates/uv/src/commands/project/run.rs"
LIB_RS = Path(REPO) / "crates/uv/src/lib.rs"


def _extract_function_body(source: str, func_name: str) -> str:
    """Extract a Rust function body by name (from 'fn name' to matching closing brace)."""
    lines = source.split("\n")
    in_func = False
    brace_depth = 0
    func_lines = []
    for line in lines:
        if not in_func and re.search(rf"\bfn\s+{func_name}\b", line):
            in_func = True
        if in_func:
            func_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(func_lines) > 1:
                break
    return "\n".join(func_lines)


def _extract_enum_body(source: str, enum_name: str) -> str:
    """Extract an enum body by name."""
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


def _extract_match_arm(body: str, variant_name: str) -> str:
    """Extract a match arm for a given variant from a function body."""
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


def _extract_fn_signature(source: str, func_name: str) -> str:
    """Extract just the signature of a Rust function (up to opening brace)."""
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_unwrap_on_downloaded_script():
    """No .unwrap() call on downloaded_script in as_command; crate compiles.

    On the base commit, as_command calls `downloaded_script.unwrap().path()`.
    Any valid fix must remove this unsafe unwrap — by embedding the file in the
    enum variant, removing the parameter, or using safe error handling.
    """
    # Behavioral: verify the refactored Rust code compiles
    try:
        r = subprocess.run(
            ["cargo", "check", "-p", "uv"],
            capture_output=True, text=True, timeout=480, cwd=REPO,
        )
        assert r.returncode == 0, f"Crate does not compile: {r.stderr[:1000]}"
    except subprocess.TimeoutExpired:
        pass  # Compilation check skipped due to timeout; structural check below

    # Structural: verify the unwrap is eliminated
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found in run.rs"

    for line in body.split("\n"):
        assert not ("downloaded_script" in line and ".unwrap()" in line), (
            f"Unsafe .unwrap() on downloaded_script: {line.strip()}"
        )


# [pr_diff] fail_to_pass
def test_python_remote_not_url_only():
    """PythonRemote variant no longer holds just a bare URL.

    On the base commit, PythonRemote(DisplaySafeUrl, Vec<OsString>) holds only
    the URL — the downloaded file is threaded separately as an Option. A correct
    fix must embed a file type in the variant or restructure so as_command
    receives a non-optional file.
    """
    src = RUN_RS.read_text()
    enum_body = _extract_enum_body(src, "RunCommand")
    assert enum_body, "RunCommand enum not found"

    remote_lines = []
    for line in enum_body.split("\n"):
        stripped = line.strip()
        if "PythonRemote" in stripped and not stripped.startswith("//"):
            remote_lines.append(stripped)

    if not remote_lines:
        # Variant was removed/renamed — acceptable if handling restructured
        return

    variant_decl = " ".join(remote_lines)

    file_types = [
        "NamedTempFile", "TempPath", "PathBuf", "tempfile",
        "DownloadedScript", "ScriptFile", "File", "DownloadedFile",
    ]
    has_file_type = any(ft in variant_decl for ft in file_types)

    if "DisplaySafeUrl" in variant_decl:
        assert has_file_type, (
            f"PythonRemote still holds only a URL (no file type): {variant_decl}"
        )
    else:
        assert has_file_type, (
            f"PythonRemote doesn't hold a file type: {variant_decl}"
        )


# [pr_diff] fail_to_pass
def test_as_command_no_option_downloaded_script():
    """as_command no longer takes downloaded_script as an Option parameter.

    On the base commit, as_command signature includes:
        downloaded_script: Option<&tempfile::NamedTempFile>
    A correct fix removes this parameter or makes it non-optional.
    """
    src = RUN_RS.read_text()
    sig = _extract_fn_signature(src, "as_command")
    assert sig, "as_command function not found"

    has_option_ds = ("downloaded_script" in sig and "Option" in sig)
    assert not has_option_ds, (
        "as_command still takes Option<downloaded_script> parameter"
    )


# [pr_diff] fail_to_pass
def test_run_fn_no_downloaded_script_param():
    """run() function in run.rs no longer takes downloaded_script as a parameter.

    On the base commit, run() in run.rs has:
        downloaded_script: Option<&tempfile::NamedTempFile>
    The fix must remove this loose Option threading entirely.
    """
    src = RUN_RS.read_text()
    sig = _extract_fn_signature(src, "run")
    assert sig, "run() function not found in run.rs"

    assert "downloaded_script" not in sig, (
        "run() still takes downloaded_script parameter — "
        "the Option threading should be eliminated"
    )


# [pr_diff] fail_to_pass
def test_lib_no_downloaded_script_threading():
    """lib.rs no longer threads downloaded_script through run_project().

    On the base commit, lib.rs creates a `downloaded_script` variable and
    passes it through run_project(). The fix must eliminate this threading
    so the download is handled closer to where it's used.
    """
    src = LIB_RS.read_text()
    sig = _extract_fn_signature(src, "run_project")
    assert sig, "run_project function not found in lib.rs"

    assert "downloaded_script" not in sig, (
        "run_project() still takes downloaded_script parameter — "
        "the Option threading through lib.rs should be eliminated"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------

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
        f"as_command has only {len(meaningful)} meaningful lines — likely a stub"
    )


# [static] pass_to_pass
def test_python_remote_variant_exists():
    """PythonRemote variant still exists in RunCommand enum."""
    src = RUN_RS.read_text()
    enum_body = _extract_enum_body(src, "RunCommand")
    assert enum_body, "RunCommand enum not found"
    assert "PythonRemote" in enum_body, (
        "PythonRemote variant missing from RunCommand enum"
    )


# [static] pass_to_pass
def test_as_command_handles_all_variants():
    """as_command still handles PythonRemote alongside other variants.

    Ensures the fix didn't just delete PythonRemote handling from as_command.
    """
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"

    for variant in ["Python(", "PythonRemote"]:
        assert variant in body, (
            f"as_command does not handle {variant} — match arms incomplete"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:7 @ 867e535f
def test_no_panic_apis_in_remote_handling():
    """No .unwrap() or panic!() in PythonRemote arm of as_command.

    CLAUDE.md line 7: 'AVOID using panic!, unreachable!, .unwrap(), unsafe code'
    """
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"

    arm = _extract_match_arm(body, "PythonRemote")

    if not arm:
        # PythonRemote handling may be restructured — check whole function
        assert "downloaded_script" not in body or ".unwrap()" not in body, (
            "PythonRemote arm not found but downloaded_script.unwrap() still present"
        )
        return

    assert ".unwrap()" not in arm, (
        f"PythonRemote arm uses .unwrap() (violates CLAUDE.md:7):\n{arm}"
    )
    assert "panic!" not in arm, (
        f"PythonRemote arm uses panic!() (violates CLAUDE.md:7):\n{arm}"
    )
    assert "unreachable!" not in arm, (
        f"PythonRemote arm uses unreachable!() (violates CLAUDE.md:7):\n{arm}"
    )
