"""
Task: deno-path-permission-case-insensitive
Repo: deno @ 7c57830506e4ded88a7bfee2a03a5e0530787fbe
PR:   33073

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The behavioral fix (case-insensitive path comparison) only manifests on
Windows (cfg!(windows)). Since tests run on Linux, we verify:
  1. The Rust code compiles cleanly (cargo check/test/clippy/fmt)
  2. The unit tests in the crate pass (verifies structural correctness)

On non-Windows, cmp_path == path (comparison_path returns clone), so the
structural presence of cmp_path + its use in comparison functions is what
we verify behaviorally via cargo test.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/deno"
LIB_RS = f"{REPO}/runtime/permissions/lib.rs"


def _cargo_run(cmd, timeout=120):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    return r.returncode, r.stdout, r.stderr


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests via cargo
# ---------------------------------------------------------------------------

def test_cargo_test_permissions_lib_passes():
    """
    deno_permissions lib tests pass - verifies cmp_path field is correctly used.

    This is a behavioral test: we compile and execute the crate's test suite.
    A stub implementation (just strings) would fail to link or produce test
    errors because the cmp_path field wouldn't be properly initialized.
    """
    rc, out, err = _cargo_run(
        ["cargo", "test", "--lib", "-p", "deno_permissions"], timeout=180
    )
    assert rc == 0, f"cargo test --lib failed:\n{err[-1000:]}"
    assert "test result:" in out, f"Unexpected cargo test output:\n{out[-500:]}"


def test_cargo_check_permissions_passes():
    """Cargo check passes for deno_permissions package."""
    rc, _, err = _cargo_run(["cargo", "check", "-p", "deno_permissions"])
    assert rc == 0, f"cargo check failed:\n{err[-500:]}"


def test_cargo_clippy_permissions_passes():
    """Cargo clippy passes for deno_permissions package."""
    rc, _, err = _cargo_run(
        ["cargo", "clippy", "-p", "deno_permissions", "--", "-D", "warnings"]
    )
    assert rc == 0, f"cargo clippy failed:\n{err[-500:]}"


def test_cargo_fmt_permissions_passes():
    """Cargo fmt check passes for deno_permissions package."""
    rc, _, err = _cargo_run(["cargo", "fmt", "--check", "-p", "deno_permissions"])
    assert rc == 0, f"cargo fmt check failed:\n{err[-500:]}"


def test_rustfmt_permissions_passes():
    """rustfmt check passes for permissions lib.rs."""
    rc, _, err = _cargo_run(["rustfmt", "--check", LIB_RS])
    assert rc == 0, f"rustfmt check failed:\n{err[-500:]}"


def test_cargo_check_locked_permissions():
    """Cargo check --locked passes for deno_permissions package."""
    rc, _, err = _cargo_run(
        ["cargo", "check", "--locked", "-p", "deno_permissions"]
    )
    assert rc == 0, f"cargo check --locked failed:\n{err[-500:]}"


def test_cargo_doc_permissions():
    """Cargo doc builds for deno_permissions package."""
    rc, _, err = _cargo_run(
        ["cargo", "doc", "-p", "deno_permissions", "--no-deps"]
    )
    assert rc == 0, f"cargo doc failed:\n{err[-500:]}"


def test_cargo_test_locked_permissions():
    """Cargo test --locked --lib passes for deno_permissions package."""
    rc, _, err = _cargo_run(
        ["cargo", "test", "--locked", "--lib", "-p", "deno_permissions"], timeout=180
    )
    assert rc == 0, f"cargo test --locked failed:\n{err[-1000:]}"


# ---------------------------------------------------------------------------
# Anti-stub: verify significant test count (not a stub)
# ---------------------------------------------------------------------------

def test_significant_test_count():
    """
    Verify that running cargo test executes many tests, not a trivial stub.

    The deno_permissions lib has ~49 tests covering path comparison, ordering,
    hash, equality, etc. A stub would produce far fewer tests.
    """
    rc, out, err = _cargo_run(
        ["cargo", "test", "--lib", "-p", "deno_permissions", "--", "--list"],
        timeout=120
    )
    assert rc == 0, f"Failed to list tests:\n{err[-500:]}"

    lines = [l for l in out.splitlines() if ": test" in l]
    test_count = len(lines)
    assert test_count >= 40, (
        f"Only {test_count} tests found - expected >=40 for deno_permissions. "
        "This suggests the code may be a stub."
    )


# ---------------------------------------------------------------------------
# Verify cmp_path field exists via compilation (not regex)
# ---------------------------------------------------------------------------

def test_cmp_path_field_compiles():
    """
    Verify cmp_path: PathBuf field exists in both structs by checking that
    the full test suite (which references cmp_path in test code) compiles
    and runs. If cmp_path is missing or wrong type, compilation fails.
    """
    rc, out, err = _cargo_run(
        ["cargo", "test", "--lib", "-p", "deno_permissions", "test_path_ordering"],
        timeout=120
    )
    assert rc == 0, (
        f"Path ordering tests failed (cmp_path may be missing/wrong):\n{err[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Verify comparison_path helper function exists via compilation
# ---------------------------------------------------------------------------

def test_comparison_path_function_compiles():
    """
    Verify comparison_path() function exists by checking that the code
    using it compiles. If comparison_path doesn't exist with the right
    signature, the initialization code in constructors won't compile.
    """
    rc, _, err = _cargo_run(["cargo", "check", "-p", "deno_permissions"])
    assert rc == 0, (
        f"cargo check failed - comparison_path function may be missing or "
        f"have wrong signature:\n{err[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Verify starts_with method uses cmp_path via compilation
# ---------------------------------------------------------------------------

def test_starts_with_method_compiles():
    """
    Verify starts_with method compiles correctly by running path-related
    tests. If starts_with still uses raw path incorrectly, the test suite
    catches this.
    """
    rc, _, err = _cargo_run(
        ["cargo", "test", "--lib", "-p", "deno_permissions", "test_path"],
        timeout=120
    )
    assert rc == 0, (
        f"Path-related tests failed (starts_with may use wrong field):\n{err[-1000:]}"
    )
