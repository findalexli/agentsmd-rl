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


def _extract_function_body(source: str, func_name: str) -> str:
    """Extract a Rust function body by name (from 'fn name' to matching closing brace).
    AST-only because: Rust code cannot be called from Python.
    """
    lines = source.split("\n")
    in_func = False
    brace_depth = 0
    func_lines = []
    for line in lines:
        if re.search(rf"fn\s+{func_name}\b", line):
            in_func = True
        if in_func:
            func_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(func_lines) > 1:
                break
    return "\n".join(func_lines)


def _extract_enum_body(source: str, enum_name: str) -> str:
    """Extract an enum body by name.
    AST-only because: Rust code cannot be called from Python.
    """
    lines = source.split("\n")
    in_enum = False
    brace_depth = 0
    enum_lines = []
    for line in lines:
        if re.search(rf"enum\s+{enum_name}\b", line):
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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Modified crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_unwrap_on_downloaded_script():
    """No .unwrap() call on downloaded_script in as_command.

    AST-only because: Rust code cannot be called from Python.

    On the base commit, as_command calls `downloaded_script.unwrap().path()`.
    Any valid fix must remove this unsafe unwrap — by embedding the file in the
    enum variant, removing the parameter, or using safe error handling.
    """
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

    AST-only because: Rust code cannot be called from Python.

    On the base commit, PythonRemote(DisplaySafeUrl, Vec<OsString>) holds only
    the URL — the downloaded file is threaded separately as an Option. A correct
    fix either:
    - Embeds the file directly in the variant (gold patch)
    - Removes PythonRemote and uses PythonScript after download
    - Adds a file field alongside the URL
    - Restructures so as_command receives a non-optional file
    """
    src = RUN_RS.read_text()
    enum_body = _extract_enum_body(src, "RunCommand")
    assert enum_body, "RunCommand enum not found"

    # Find the PythonRemote variant line(s)
    remote_lines = []
    for line in enum_body.split("\n"):
        stripped = line.strip()
        if "PythonRemote" in stripped and not stripped.startswith("//"):
            remote_lines.append(stripped)

    if not remote_lines:
        # Variant was removed/renamed — acceptable if PythonRemote handling
        # was restructured (e.g., converted to PythonScript after download)
        return

    variant_decl = " ".join(remote_lines)

    file_types = [
        "NamedTempFile", "TempPath", "PathBuf", "tempfile",
        "DownloadedScript", "ScriptFile", "File", "DownloadedFile",
    ]
    has_file_type = any(ft in variant_decl for ft in file_types)

    # If it still holds a DisplaySafeUrl, it must ALSO hold a file type
    if "DisplaySafeUrl" in variant_decl:
        assert has_file_type, (
            f"PythonRemote still holds only a URL (no file type): {variant_decl}"
        )
    else:
        # URL was removed — must hold a file type instead
        assert has_file_type, (
            f"PythonRemote doesn't hold a file type: {variant_decl}"
        )


# [pr_diff] fail_to_pass
def test_as_command_no_option_downloaded_script():
    """as_command no longer takes downloaded_script as an Option parameter.

    AST-only because: Rust code cannot be called from Python.

    On the base commit, as_command signature includes:
        downloaded_script: Option<&tempfile::NamedTempFile>
    A correct fix removes this parameter or makes it non-optional.
    """
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"

    # Extract the function signature (everything before the first { at depth 1)
    sig_lines = []
    for line in body.split("\n"):
        sig_lines.append(line)
        if "{" in line:
            break
    sig = " ".join(sig_lines)

    # Fail if signature still has Option<...downloaded_script...>
    has_option_ds = (
        "downloaded_script" in sig and "Option" in sig
    )
    assert not has_option_ds, (
        f"as_command still takes Option<downloaded_script> parameter"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_as_command_not_stub():
    """as_command has a real implementation with meaningful logic.

    AST-only because: Rust code cannot be called from Python.
    """
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"

    meaningful = [
        line for line in body.split("\n")
        if line.strip()
        and not line.strip().startswith("//")
        and line.strip() not in ("{", "}")
    ]
    assert len(meaningful) >= 8, (
        f"as_command has only {len(meaningful)} meaningful lines — likely a stub"
    )


# [static] pass_to_pass
def test_python_remote_variant_exists():
    """PythonRemote variant still exists in RunCommand enum.

    AST-only because: Rust code cannot be called from Python.
    """
    src = RUN_RS.read_text()
    enum_body = _extract_enum_body(src, "RunCommand")
    assert enum_body, "RunCommand enum not found"
    assert "PythonRemote" in enum_body, (
        "PythonRemote variant missing from RunCommand enum"
    )


# [static] pass_to_pass
def test_as_command_handles_all_variants():
    """as_command still handles PythonRemote alongside other variants.

    AST-only because: Rust code cannot be called from Python.

    Ensures the fix didn't just delete PythonRemote handling from as_command.
    """
    src = RUN_RS.read_text()
    body = _extract_function_body(src, "as_command")
    assert body, "as_command function not found"

    # as_command must handle key variants — check at least Python and PythonRemote
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

    AST-only because: Rust code cannot be called from Python.

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
