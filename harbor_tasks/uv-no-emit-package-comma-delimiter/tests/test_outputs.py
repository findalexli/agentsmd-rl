"""
Task: uv-no-emit-package-comma-delimiter
Repo: astral-sh/uv @ 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c
PR:   #18565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

REPO = "/repo"
CLI_FILE = f"{REPO}/crates/uv-cli/src/lib.rs"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def delimiter_check_output():
    """Build and run a Rust binary that inspects clap's compiled command spec."""
    examples_dir = Path(REPO) / "crates" / "uv-cli" / "examples"
    examples_dir.mkdir(exist_ok=True)
    test_rs = examples_dir / "comma_delim_check.rs"
    test_rs.write_text(
        """\
use clap::{Args, Command};

fn has_comma_delimiter(cmd: &Command, arg_id: &str) -> bool {
    cmd.get_arguments()
        .find(|a| a.get_id().as_str() == arg_id)
        .map_or(false, |a| a.get_value_delimiter() == Some(','))
}

fn build_cmd<T: Args>() -> Command {
    let mut cmd = Command::new("test");
    cmd = T::augment_args(cmd);
    cmd
}

fn main() {
    let cmd = build_cmd::<uv_cli::ExportArgs>();
    println!(
        "EXPORT_NO_EMIT:{}",
        if has_comma_delimiter(&cmd, "no_emit_package") { "PASS" } else { "FAIL" }
    );
    println!(
        "EXPORT_ONLY_EMIT:{}",
        if has_comma_delimiter(&cmd, "only_emit_package") { "PASS" } else { "FAIL" }
    );

    let cmd2 = build_cmd::<uv_cli::PipCompileArgs>();
    println!(
        "PIPCOMPILE_NO_EMIT:{}",
        if has_comma_delimiter(&cmd2, "no_emit_package") { "PASS" } else { "FAIL" }
    );
}
"""
    )

    r = subprocess.run(
        ["cargo", "run", "-p", "uv-cli", "--example", "comma_delim_check"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    stdout = r.stdout.decode()
    stderr = r.stderr.decode()

    # Clean up test artifact
    test_rs.unlink(missing_ok=True)
    try:
        examples_dir.rmdir()
    except OSError:
        pass

    yield stdout, stderr, r.returncode


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """uv-cli crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-cli"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral via compiled clap command spec
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_export_no_emit_package_comma_delimiter(delimiter_check_output):
    """ExportArgs no_emit_package accepts comma-separated values via value_delimiter."""
    stdout, stderr, rc = delimiter_check_output
    assert "EXPORT_NO_EMIT:PASS" in stdout, (
        f"ExportArgs no_emit_package missing comma delimiter.\nstdout: {stdout}\nstderr: {stderr[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_export_only_emit_package_comma_delimiter(delimiter_check_output):
    """ExportArgs only_emit_package accepts comma-separated values via value_delimiter."""
    stdout, stderr, rc = delimiter_check_output
    assert "EXPORT_ONLY_EMIT:PASS" in stdout, (
        f"ExportArgs only_emit_package missing comma delimiter.\nstdout: {stdout}\nstderr: {stderr[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_pipcompile_no_emit_package_comma_delimiter(delimiter_check_output):
    """PipCompileArgs no_emit_package accepts comma-separated values via value_delimiter."""
    stdout, stderr, rc = delimiter_check_output
    assert "PIPCOMPILE_NO_EMIT:PASS" in stdout, (
        f"PipCompileArgs no_emit_package missing comma delimiter.\nstdout: {stdout}\nstderr: {stderr[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_aliases_preserved():
    """Existing aliases (no-install-package, only-install-package, unsafe-package) still present."""
    content = Path(CLI_FILE).read_text()
    assert "no-install-package" in content, "no-install-package alias missing from ExportArgs"
    assert "only-install-package" in content, "only-install-package alias missing from ExportArgs"
    assert "unsafe-package" in content, "unsafe-package alias missing from PipCompileArgs"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c
def test_no_prohibited_patterns_in_changes():
    """No .unwrap(), panic!, unreachable!, or unsafe introduced in modified code."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", CLI_FILE],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]

    prohibited = [".unwrap()", "panic!", "unreachable!", "unsafe "]
    for pattern in prohibited:
        hits = [l for l in added_lines if pattern in l]
        assert len(hits) == 0, (
            f"Found prohibited pattern '{pattern}' in added lines:\n" +
            "\n".join(hits)
        )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c
def test_no_allow_attribute_in_changes():
    """Uses #[expect()] instead of #[allow()] for clippy suppressions."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", CLI_FILE],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    allow_hits = [l for l in added_lines if "#[allow(" in l]
    assert len(allow_hits) == 0, (
        f"Found #[allow()] in added lines (use #[expect()] instead):\n" +
        "\n".join(allow_hits)
    )
