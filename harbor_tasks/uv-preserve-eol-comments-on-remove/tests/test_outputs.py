"""Behavioral tests for astral-sh/uv#18557.

The PR teaches `remove_dependency` in `crates/uv-workspace/src/pyproject_mut.rs`
to preserve end-of-line comments when an adjacent dependency is removed.
We exercise the bug through the public `PyProjectTomlMut::remove_dependency`
API by writing a Rust integration test file into the uv-workspace crate and
running it via `cargo test`.

Each `def test_*` function corresponds 1:1 to an entry in eval_manifest.yaml.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/uv")
RUST_TEST_FILE = REPO / "crates" / "uv-workspace" / "tests" / "comment_preservation.rs"
CARGO_ENV = {**os.environ, "CARGO_TERM_COLOR": "never", "RUST_BACKTRACE": "1"}

RUST_TEST_SOURCE = r'''//! Integration tests for end-of-line comment preservation when removing
//! dependencies from `pyproject.toml`. These exercise the public
//! `PyProjectTomlMut::remove_dependency` API.

use std::str::FromStr;
use uv_normalize::PackageName;
use uv_workspace::pyproject_mut::{DependencyTarget, PyProjectTomlMut};

fn remove(toml: &str, dep: &str) -> String {
    let mut doc =
        PyProjectTomlMut::from_toml(toml, DependencyTarget::PyProjectToml).expect("parse toml");
    let name = PackageName::from_str(dep).expect("parse package name");
    doc.remove_dependency(&name).expect("remove dependency");
    doc.to_string()
}

#[test]
fn eol_comment_on_previous_item_is_preserved() {
    let toml = r#"[project]
name = "x"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.4.3", # essential comment
    "requests>=2.32.5",
]
"#;
    let result = remove(toml, "requests");
    assert!(
        result.contains("\"numpy>=2.4.3\", # essential comment"),
        "EOL comment lost when removing the trailing item:\n{result}"
    );
    assert!(
        !result.contains("\"requests"),
        "requests dependency entry was not removed:\n{result}"
    );
}

#[test]
fn eol_comment_on_previous_item_preserved_in_middle_removal() {
    let toml = r#"[project]
name = "x"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.4.3", # numpy comment
    "requests>=2.32.5",
    "flask>=3.0.0",
]
"#;
    let result = remove(toml, "requests");
    assert!(
        result.contains("\"numpy>=2.4.3\", # numpy comment"),
        "Comment on `numpy` lost when removing middle item:\n{result}"
    );
    assert!(result.contains("\"flask>=3.0.0\""), "flask was lost:\n{result}");
    assert!(
        !result.contains("\"requests"),
        "requests dependency entry was not removed:\n{result}"
    );
}

#[test]
fn own_line_comment_above_removed_item_is_preserved() {
    let toml = r#"[project]
name = "x"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.4.3",
    # This is a comment about requests
    "requests>=2.32.5",
]
"#;
    let result = remove(toml, "requests");
    assert!(
        result.contains("# This is a comment about requests"),
        "Own-line comment lost when removing requests:\n{result}"
    );
    assert!(
        !result.contains("\"requests"),
        "requests dependency entry was not removed:\n{result}"
    );
}

#[test]
fn eol_comment_on_previous_item_preserved_when_removing_last_item() {
    let toml = r#"[project]
name = "x"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "numpy>=2.4.3", # comment on numpy
    "requests>=2.32.5",
]
"#;
    let result = remove(toml, "requests");
    assert!(
        result.contains("\"numpy>=2.4.3\", # comment on numpy"),
        "EOL comment on previous item lost when removing last item:\n{result}"
    );
    assert!(
        !result.contains("\"requests"),
        "requests dependency entry was not removed:\n{result}"
    );
}

#[test]
fn comment_order_preserved_for_multiple_adjacent_matches() {
    let toml = r#"[project]
name = "x"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # comment on iniconfig
    "typing-extensions>=4.0.0 ; python_version < '3.11'", # comment on first typing-extensions
    "typing-extensions>=4.0.0 ; python_version >= '3.11'",
    "sniffio>=1.3.0",
]
"#;
    let result = remove(toml, "typing-extensions");
    assert!(
        result.contains("\"iniconfig>=2.0.0\", # comment on iniconfig"),
        "iniconfig EOL comment lost:\n{result}"
    );
    assert!(
        result.contains("# comment on first typing-extensions"),
        "First typing-extensions comment lost:\n{result}"
    );
    assert!(
        !result.contains("\"typing-extensions"),
        "typing-extensions dependency entries were not fully removed:\n{result}"
    );
    let iniconfig_idx = result
        .find("# comment on iniconfig")
        .expect("iniconfig comment present");
    let te_idx = result
        .find("# comment on first typing-extensions")
        .expect("typing-extensions comment present");
    assert!(
        iniconfig_idx < te_idx,
        "Comment ordering changed (iniconfig should precede typing-extensions):\n{result}"
    );
}
'''


def _ensure_rust_test_installed() -> None:
    """Write the Rust integration test into the uv-workspace crate (idempotent)."""
    RUST_TEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    if (
        not RUST_TEST_FILE.exists()
        or RUST_TEST_FILE.read_text() != RUST_TEST_SOURCE
    ):
        RUST_TEST_FILE.write_text(RUST_TEST_SOURCE)


def _run_rust_test(test_name: str, *, timeout: int = 600) -> subprocess.CompletedProcess:
    _ensure_rust_test_installed()
    cmd = [
        "cargo",
        "test",
        "-p",
        "uv-workspace",
        "--test",
        "comment_preservation",
        "--",
        "--exact",
        "--nocapture",
        test_name,
    ]
    return subprocess.run(
        cmd,
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ────────────────────────────── fail-to-pass ──────────────────────────────


def test_eol_comment_on_previous_item_is_preserved():
    """Removing a trailing dep must keep the prior dep's end-of-line comment."""
    r = _run_rust_test("eol_comment_on_previous_item_is_preserved")
    assert r.returncode == 0, (
        f"Rust test failed.\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout, r.stdout[-2000:]


def test_eol_comment_on_previous_item_preserved_in_middle_removal():
    """Removing a middle dep keeps prior dep's end-of-line comment intact."""
    r = _run_rust_test("eol_comment_on_previous_item_preserved_in_middle_removal")
    assert r.returncode == 0, (
        f"Rust test failed.\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout, r.stdout[-2000:]


def test_own_line_comment_above_removed_item_is_preserved():
    """An own-line comment immediately above the removed dep must be retained."""
    r = _run_rust_test("own_line_comment_above_removed_item_is_preserved")
    assert r.returncode == 0, (
        f"Rust test failed.\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout, r.stdout[-2000:]


def test_eol_comment_on_previous_item_preserved_when_removing_last_item():
    """Removing the LAST array item must keep the previous item's end-of-line comment."""
    r = _run_rust_test("eol_comment_on_previous_item_preserved_when_removing_last_item")
    assert r.returncode == 0, (
        f"Rust test failed.\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout, r.stdout[-2000:]


def test_comment_order_preserved_for_multiple_adjacent_matches():
    """Removing multiple adjacent matches must preserve original comment order."""
    r = _run_rust_test("comment_order_preserved_for_multiple_adjacent_matches")
    assert r.returncode == 0, (
        f"Rust test failed.\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout, r.stdout[-2000:]


# ────────────────────────────── pass-to-pass ──────────────────────────────


def test_uv_workspace_compiles():
    """`cargo check -p uv-workspace` succeeds (regression guard against breakage)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-workspace", "--lib"],
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"`cargo check` failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_existing_unit_tests_pass():
    """Pre-existing uv-workspace unit tests for `pyproject_mut` continue to pass."""
    r = subprocess.run(
        [
            "cargo",
            "test",
            "-p",
            "uv-workspace",
            "--lib",
            "--",
            "pyproject_mut::test::reformat_preserves_inline_comment_spacing",
        ],
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"Existing unit test failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )
