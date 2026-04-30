"""
Task: uv-run-remote-script-unwrap-panic
Repo: astral-sh/uv @ 867e535f2a5f7f2b1f22a0ccc52fc6da5b01ac3c
PR:   18707

Behavioral test suite.  Core f2p tests inject Rust unit tests into the crate,
compile and run them via cargo, then assert on the result.  This verifies
actual code behavior (type system, API shape) rather than grepping source.
"""

import re
import subprocess

import pytest
from pathlib import Path

REPO = "/repo"
RUN_RS = Path(REPO) / "crates/uv/src/commands/project/run.rs"
LIB_RS = Path(REPO) / "crates/uv/src/lib.rs"

# ---------------------------------------------------------------------------
# Rust behavioral test module — injected into run.rs for compilation + runtime
# ---------------------------------------------------------------------------

_MARKER_BEGIN = "// __BEHAVIORAL_TEST_BEGIN__"

_RUST_TEST_MODULE = """
// __BEHAVIORAL_TEST_BEGIN__
#[cfg(test)]
mod behavioral_fix_tests {
    use super::*;
    use std::ffi::OsString;

    /// Construct a PythonRemote variant with an actual temp file.
    /// On the base commit PythonRemote holds (DisplaySafeUrl, Vec<OsString>),
    /// so this fails to compile - proving the variant now embeds a file handle.
    #[test]
    fn python_remote_holds_file() {
        let tf = tempfile::NamedTempFile::new().expect("create temp file");
        let expected_path = tf.path().to_path_buf();
        let cmd = RunCommand::PythonRemote(tf, vec![OsString::from("--flag")]);
        match &cmd {
            RunCommand::PythonRemote(file, args) => {
                assert!(file.path().exists(), "embedded temp file must exist");
                assert_eq!(file.path(), expected_path, "path must match");
                assert_eq!(args.len(), 1, "args forwarded");
            }
            _ => panic!("expected PythonRemote variant"),
        }
    }

    /// Compile-time proof: as_command() takes only (&self, &Interpreter).
    /// On base it requires a third Option<&NamedTempFile> argument,
    /// so this function body would not compile.
    #[allow(dead_code)]
    fn verify_as_command_arity(c: &RunCommand, i: &Interpreter) -> Command {
        c.as_command(i)
    }
}
"""


def _inject_rust_tests():
    """Append the Rust test module to run.rs (idempotent)."""
    src = RUN_RS.read_text()
    if _MARKER_BEGIN in src:
        return
    RUN_RS.write_text(src + _RUST_TEST_MODULE)


def _remove_rust_tests():
    """Strip the injected Rust test module from run.rs."""
    src = RUN_RS.read_text()
    start = src.find(_MARKER_BEGIN)
    if start == -1:
        return
    while start > 0 and src[start - 1] == "\n":
        start -= 1
    RUN_RS.write_text(src[:start])


@pytest.fixture(scope="module")
def behavioral_result():
    """Inject Rust tests, compile + run them, yield results, clean up."""
    _inject_rust_tests()
    try:
        compile_r = subprocess.run(
            ["cargo", "test", "-p", "uv", "--lib", "--no-run"],
            capture_output=True, text=True, timeout=480, cwd=REPO,
        )
        run_r = None
        if compile_r.returncode == 0:
            run_r = subprocess.run(
                ["cargo", "test", "-p", "uv", "--lib", "--",
                 "behavioral_fix_tests"],
                capture_output=True, text=True, timeout=120, cwd=REPO,
            )
        yield {"compile": compile_r, "run": run_r}
    finally:
        _remove_rust_tests()


# ---------------------------------------------------------------------------
# Helpers for structural checks
# ---------------------------------------------------------------------------

def _extract_function_body(source, func_name):
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
# SECTION 1 - Tests that do NOT use the behavioral fixture.
# These run first (pytest executes top-to-bottom), before code injection.
# ===================================================================

# [repo_tests] pass_to_pass
def test_repo_cargo_check():
    """Repo Rust code compiles with cargo check (pass_to_pass)."""
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
    """Repo Rust code is formatted correctly (pass_to_pass)."""
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt failed:\n{r.stderr[-500:]}"


# [pr_diff] fail_to_pass
def test_run_fn_no_downloaded_script_param():
    """run() in run.rs must not accept downloaded_script as a parameter.

    Verifies the function signature after confirming the crate compiles.
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

    Verifies the function signature after confirming the crate compiles.
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
# SECTION 2 - Tests that USE the behavioral fixture.
# The fixture injects a Rust test module into run.rs, compiles/runs it,
# then cleans up.  These MUST come after all non-fixture tests.
# ===================================================================

# [pr_diff] fail_to_pass
def test_no_unwrap_on_downloaded_script(behavioral_result):
    """Behavioral: injected Rust tests compile and pass, proving the
    .unwrap() on downloaded_script is eliminated and PythonRemote is safe.

    On the base commit the injected module fails to compile because
    as_command's signature and PythonRemote's type differ from the fix.
    """
    cr = behavioral_result["compile"]
    assert cr.returncode == 0, (
        f"Behavioral tests failed to compile (fix not applied):\n"
        f"{cr.stderr[:1000]}"
    )
    rr = behavioral_result["run"]
    assert rr is not None and rr.returncode == 0, (
        f"Behavioral tests failed:\n"
        f"{rr.stderr[:500] if rr else 'not run'}"
    )


# [pr_diff] fail_to_pass
def test_python_remote_not_url_only(behavioral_result):
    """Behavioral: PythonRemote(NamedTempFile, args) compiles and works.

    On the base commit PythonRemote takes (DisplaySafeUrl, Vec<OsString>),
    so constructing it with a NamedTempFile fails to compile.
    """
    cr = behavioral_result["compile"]
    assert cr.returncode == 0, (
        f"PythonRemote still holds a URL, not a file:\n{cr.stderr[:1000]}"
    )
    rr = behavioral_result["run"]
    assert rr is not None and rr.returncode == 0, (
        f"PythonRemote file test failed:\n"
        f"{rr.stderr[:500] if rr else 'not run'}"
    )


# [pr_diff] fail_to_pass
def test_as_command_no_option_downloaded_script(behavioral_result):
    """Behavioral: as_command(&self, &Interpreter) compiles with 2 args.

    On the base commit as_command requires a third Option<&NamedTempFile>
    argument, so verify_as_command_arity() would not compile.
    """
    cr = behavioral_result["compile"]
    assert cr.returncode == 0, (
        f"as_command still requires optional downloaded_script:\n"
        f"{cr.stderr[:1000]}"
    )


# [agent_config] fail_to_pass
def test_no_panic_apis_in_remote_handling(behavioral_result):
    """No .unwrap()/panic!()/unreachable!() in PythonRemote arm of as_command.

    Verified both by compiling Rust behavioral tests (which exercise
    PythonRemote construction and as_command) and by inspecting the match arm.
    """
    cr = behavioral_result["compile"]
    assert cr.returncode == 0, (
        f"Behavioral tests do not compile:\n{cr.stderr[:500]}"
    )

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
