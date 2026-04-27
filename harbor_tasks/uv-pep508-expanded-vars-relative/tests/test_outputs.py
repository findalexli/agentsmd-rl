"""Behavioral tests for the PEP 508 URL expanded-variable regression
(astral-sh/uv#18680).

The PR's symptom is that `VerbatimUrl::was_given_absolute()` returns `true`
for PEP 508 URLs that became absolute only because environment variables
expanded to absolute paths (e.g., `file://${PWD}/foo`). Such URLs should
be treated as relative so existing usecases that rely on `${PWD}` or
`${PROJECT_ROOT}` continue to work after lock-file generation.

We verify by adding an integration test (`tests/expanded_vars_test.rs`)
to the `uv-pep508` crate and running it via `cargo test`. Some
pass-to-pass tests also exercise the existing `cargo build`/`cargo check`
on the crate so style/compile regressions surface.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/uv")
PEP508_DIR = REPO / "crates" / "uv-pep508"
TESTS_DIR = PEP508_DIR / "tests"
TEST_FILE = TESTS_DIR / "expanded_vars_test.rs"

# Rust integration test that pins the f2p behavior. We import only public API
# from `uv-pep508` (the trait `Pep508Url` and `VerbatimUrl`).
EXPANDED_VARS_TEST = r"""
//! Behavioral tests for VerbatimUrl::was_given_absolute() on PEP 508 URLs
//! whose original `given` value contained environment variable references
//! that were expanded at parse time. See astral-sh/uv#18680.

use std::path::Path;

use uv_pep508::{Pep508Url, VerbatimUrl};

fn parse(input: &str) -> VerbatimUrl {
    <VerbatimUrl as Pep508Url>::parse_url(input, None)
        .expect("parse_url should succeed")
}

fn parse_with_dir(input: &str, dir: &Path) -> VerbatimUrl {
    <VerbatimUrl as Pep508Url>::parse_url(input, Some(dir))
        .expect("parse_url should succeed")
}

#[test]
fn pep508_file_url_with_expanded_var_is_not_absolute() {
    // SAFETY: Tests in this binary execute serially; we set+read the env var
    // ourselves and don't spawn additional threads that depend on it.
    unsafe {
        std::env::set_var("UV_TEST_PEP508_VAR_A", "/abs/path");
    }

    let url = parse("file://${UV_TEST_PEP508_VAR_A}/foo");

    // After expansion the URL becomes file:///abs/path/foo which would
    // otherwise be treated as absolute. Because it originated as a PEP 508
    // URL with an expanded variable, was_given_absolute must return false.
    assert!(
        !url.was_given_absolute(),
        "file:// URL with an expanded env var should NOT be reported as absolute, \
         was_given_absolute returned true"
    );
}

#[test]
fn pep508_three_slash_file_url_with_expanded_var_is_not_absolute() {
    // Mirrors the `c @ file:///${PROJECT_ROOT}/c` shape from the PR. Even
    // though the expansion produces a syntactically absolute file URL, it
    // must NOT be reported as absolute because the original given form
    // contained an expanded variable.
    unsafe {
        std::env::set_var("UV_TEST_PEP508_VAR_C", "abs/path");
    }

    let url = parse("file:///${UV_TEST_PEP508_VAR_C}/foo");

    assert!(
        !url.was_given_absolute(),
        "file:/// URL with an expanded env var should NOT be reported as absolute"
    );
}

#[test]
fn pep508_file_url_without_vars_is_absolute() {
    let url = parse("file:///some/abs/path/foo");
    assert!(
        url.was_given_absolute(),
        "plain file:// URL pointing at an absolute path should be absolute"
    );
}

#[test]
fn pep508_file_url_with_unrelated_dollar_text_is_unchanged() {
    // "$" without a variable reference does not trigger expansion.
    // Such a URL is plain absolute and should stay absolute.
    let url = parse("file:///abs/path/with$dollar/foo");
    assert!(
        url.was_given_absolute(),
        "file:// URL containing literal '$' but no expanded vars should remain absolute"
    );
}

#[test]
fn pep508_relative_path_without_vars_is_not_absolute() {
    let working_dir = std::env::current_dir().expect("cwd");
    let url = parse_with_dir("./relative/path/foo", &working_dir);
    assert!(
        !url.was_given_absolute(),
        "plain relative path should not be reported as absolute"
    );
}
"""


def _ensure_test_file_installed() -> None:
    TESTS_DIR.mkdir(exist_ok=True)
    if TEST_FILE.exists():
        TEST_FILE.unlink()
    TEST_FILE.write_text(EXPANDED_VARS_TEST.lstrip("\n"))


def _run_cargo_test(test_binary: str, test_name: str | None = None,
                    features: str | None = None, timeout: int = 1200):
    cmd = ["cargo", "test", "-p", "uv-pep508", "--test", test_binary]
    if features:
        cmd.extend(["--features", features])
    if test_name:
        cmd.extend(["--", "--exact", test_name, "--nocapture"])
    return subprocess.run(
        cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout,
        env={**os.environ, "CARGO_TERM_COLOR": "never"},
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: target behavior
# ---------------------------------------------------------------------------

def test_pep508_file_url_with_expanded_var_is_not_absolute():
    """A file:// URL whose given form contains an expanded env var must
    NOT be reported as absolute. This is the PR's regression check."""
    _ensure_test_file_installed()
    r = _run_cargo_test(
        "expanded_vars_test",
        "pep508_file_url_with_expanded_var_is_not_absolute",
        features="non-pep508-extensions",
    )
    assert r.returncode == 0, (
        f"cargo test failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_pep508_three_slash_file_url_with_expanded_var_is_not_absolute():
    """A `file:///` URL whose given form contains an expanded env var
    (mirrors `${PROJECT_ROOT}`) must NOT be reported as absolute."""
    _ensure_test_file_installed()
    r = _run_cargo_test(
        "expanded_vars_test",
        "pep508_three_slash_file_url_with_expanded_var_is_not_absolute",
        features="non-pep508-extensions",
    )
    assert r.returncode == 0, (
        f"cargo test failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: behavior that must be preserved
# ---------------------------------------------------------------------------

def test_pep508_plain_file_url_remains_absolute():
    """A file:// URL with no variable expansion must continue to be
    reported as absolute."""
    _ensure_test_file_installed()
    r = _run_cargo_test(
        "expanded_vars_test",
        "pep508_file_url_without_vars_is_absolute",
        features="non-pep508-extensions",
    )
    assert r.returncode == 0, (
        f"cargo test failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_pep508_plain_relative_path_is_not_absolute():
    """A relative path with no variable expansion must remain non-absolute."""
    _ensure_test_file_installed()
    r = _run_cargo_test(
        "expanded_vars_test",
        "pep508_relative_path_without_vars_is_not_absolute",
        features="non-pep508-extensions",
    )
    assert r.returncode == 0, (
        f"cargo test failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_pep508_dollar_literal_url_remains_absolute():
    """A file:// URL containing a literal '$' that is not part of a
    variable reference must still be reported as absolute."""
    _ensure_test_file_installed()
    r = _run_cargo_test(
        "expanded_vars_test",
        "pep508_file_url_with_unrelated_dollar_text_is_unchanged",
        features="non-pep508-extensions",
    )
    assert r.returncode == 0, (
        f"cargo test failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_uv_pep508_crate_compiles():
    """The uv-pep508 crate must build cleanly under both feature configurations.
    Catches accidental syntax/type breakage outside of the patched callsites."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-pep508", "--tests"],
        cwd=REPO, capture_output=True, text=True, timeout=1200,
    )
    assert r.returncode == 0, (
        f"cargo check failed (default features):\n{r.stderr[-2000:]}"
    )

    r = subprocess.run(
        ["cargo", "check", "-p", "uv-pep508", "--tests",
         "--features", "non-pep508-extensions"],
        cwd=REPO, capture_output=True, text=True, timeout=1200,
    )
    assert r.returncode == 0, (
        f"cargo check failed (non-pep508-extensions):\n{r.stderr[-2000:]}"
    )


def test_uv_pep508_unit_tests_pass():
    """The uv-pep508 crate's own (lib-internal) unit tests must continue
    to pass — guards against breaking sibling code while editing
    verbatim_url.rs."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-pep508", "--lib"],
        cwd=REPO, capture_output=True, text=True, timeout=1200,
    )
    assert r.returncode == 0, (
        f"uv-pep508 lib tests failed:\n--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )
