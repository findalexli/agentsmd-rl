"""
Task: deno-child-process-numeric-fd-stdio
Repo: deno @ d198cda44b7fddb56d892a8ef2349d1630adfa37
PR:   33140

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/deno"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stdio_or_fd_enum():
    """StdioOrRid must be renamed to StdioOrFd in the process extension."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    assert re.search(r"pub\s+enum\s+StdioOrFd\b", content), \
        "Expected 'pub enum StdioOrFd' to be defined in ext/process/lib.rs"
    assert not re.search(r"\benum\s+StdioOrRid\b", content), \
        "Old 'enum StdioOrRid' should no longer exist"


# [pr_diff] fail_to_pass
def test_fd_variant_with_i32():
    """The enum must have an Fd(i32) variant instead of Rid(ResourceId)."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    # Find the enum body and check for the Fd variant
    assert re.search(r"\bFd\(i32\)", content), \
        "Expected Fd(i32) variant in StdioOrFd enum"
    assert not re.search(r"\bRid\(ResourceId\)", content), \
        "Old Rid(ResourceId) variant should be removed"


# [pr_diff] fail_to_pass
def test_as_stdio_fd_duplication():
    """as_stdio must duplicate file descriptors using libc::dup on Unix."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    assert "libc::dup(" in content, \
        "Expected libc::dup() call for fd duplication in as_stdio"
    # Should also use OwnedFd / from_raw_fd for safe ownership transfer
    assert "from_raw_fd" in content, \
        "Expected from_raw_fd for creating owned fd from dup result"


# [pr_diff] fail_to_pass
def test_child_process_stdio_struct():
    """ChildProcessStdio struct must exist in ext/io/lib.rs for handle inheritance."""
    content = Path(f"{REPO}/ext/io/lib.rs").read_text()
    assert re.search(r"pub\s+struct\s+ChildProcessStdio\b", content), \
        "Expected 'pub struct ChildProcessStdio' in ext/io/lib.rs"
    # Must hold both stdout and stderr handles
    assert re.search(r"pub\s+stdout\s*:", content), \
        "ChildProcessStdio must have a pub stdout field"
    assert re.search(r"pub\s+stderr\s*:", content), \
        "ChildProcessStdio must have a pub stderr field"


# [pr_diff] fail_to_pass
def test_extra_stdio_accepts_stdio_or_fd():
    """extra_stdio field must accept StdioOrFd to support numeric fd passthrough."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    assert re.search(r"extra_stdio\s*:\s*Vec<StdioOrFd>", content), \
        "Expected extra_stdio: Vec<StdioOrFd> in SpawnArgs"
    # Old type should be gone
    assert not re.search(r"extra_stdio\s*:\s*Vec<Stdio>", content), \
        "Old extra_stdio: Vec<Stdio> should be changed to Vec<StdioOrFd>"


# [pr_diff] fail_to_pass
def test_inherit_uses_child_process_stdio():
    """Inherit mode must borrow ChildProcessStdio from OpState, not use hardcoded Rid."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    # Fix borrows ChildProcessStdio from state when inheriting stdout/stderr
    assert "borrow::<ChildProcessStdio>" in content, \
        "Expected state.borrow::<ChildProcessStdio>() for inherit mode"
    # Old approach of constructing Rid(1)/Rid(2) should be gone
    assert "StdioOrRid::Rid(1)" not in content, \
        "Old hardcoded StdioOrRid::Rid(1) should be removed"
    assert "StdioOrRid::Rid(2)" not in content, \
        "Old hardcoded StdioOrRid::Rid(2) should be removed"


# [pr_diff] fail_to_pass
def test_file_resource_import_removed():
    """FileResource import should be removed; ChildProcessStdio imported instead."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    assert "use deno_io::fs::FileResource" not in content, \
        "FileResource import should be removed from ext/process/lib.rs"
    assert "use deno_io::ChildProcessStdio" in content, \
        "Expected import of ChildProcessStdio from deno_io"


# [pr_diff] fail_to_pass
def test_numeric_fd_deserialization():
    """Numeric values must deserialize as Fd, using i64/i32 checks not u64/ResourceId."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    # The deserialization should use as_i64 (signed) for fd validation
    assert "as_i64()" in content, \
        "Expected as_i64() for numeric fd deserialization (not as_u64)"
    # Error message should mention file descriptor, not resource id
    assert re.search(r"file descriptor", content, re.IGNORECASE), \
        "Error messages should reference 'file descriptor' not 'resource id'"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_stdio_string_deserialization_preserved():
    """String variants (inherit, piped, null) must still be handled correctly."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    for variant in ["inherit", "piped", "null", "ipc_for_internal_use"]:
        assert f'"{variant}"' in content, \
            f"Missing string variant '{variant}' in Deserialize impl"


# [static] pass_to_pass
def test_child_stdio_struct_fields():
    """ChildStdio struct must still have stdin, stdout, stderr fields."""
    content = Path(f"{REPO}/ext/process/lib.rs").read_text()
    assert re.search(r"pub\s+struct\s+ChildStdio\b", content), \
        "ChildStdio struct must exist"
    for field in ["stdin", "stdout", "stderr"]:
        assert re.search(rf"\b{field}\s*:\s*StdioOr", content), \
            f"ChildStdio must have a {field} field of type StdioOr*"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# These verify the repo's own CI commands pass on the base commit.
#
# CI commands discovered from .github/workflows/ci.generated.yml:
# - cargo check -p deno_io
# - cargo check -p deno_process
# - cargo clippy -p deno_process -p deno_io -- -D warnings
#
# Skipped commands (not suitable for p2p):
# - cargo fmt --check: requires rustfmt component, rustup sync issues
# - cargo check --all-targets: requires cmake, not installed
# - cargo test: takes too long (>120s), runs full test suite
# - cargo build: too slow for p2p gating
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_check_deno_io():
    """Cargo check deno_io package compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "deno_io"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p deno_io failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_check_deno_process():
    """Cargo check deno_process package compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "deno_process"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p deno_process failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_clippy_process_io():
    """Cargo clippy passes for process and io packages (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "deno_process", "-p", "deno_io", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"
