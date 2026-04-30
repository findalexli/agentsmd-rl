"""Behavioral tests for astral-sh/uv#18850.

Each `def test_*` maps 1:1 to a check id in eval_manifest.yaml.
We exercise `uv_pep440::VersionSpecifiers::from_str` via a small Rust
integration test we drop into `crates/uv-pep440/tests/`. The repo and
its dependency tree are pre-fetched in the Docker image, so we can
run cargo offline without network.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/uv")
TEST_DIR = REPO / "crates" / "uv-pep440" / "tests"
SCAFFOLD_TEST = TEST_DIR / "scaffold_tie_break.rs"

CARGO_ENV = {
    **os.environ,
    "CARGO_TERM_COLOR": "never",
    "CARGO_INCREMENTAL": "0",
}


def _write_scaffold_test() -> None:
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    SCAFFOLD_TEST.write_text(textwrap.dedent('''\
        use std::str::FromStr;
        use uv_pep440::VersionSpecifiers;

        // Multiple distinct singular intervals — none of these literals
        // appear in the agent-visible code, so we can detect hardcoded
        // shortcuts.
        const SINGULAR: &[(&str, &str, &str)] = &[
            (">=1.4.4, <=1.4.4", "<=1.4.4, >=1.4.4", "<=1.4.4, >=1.4.4"),
            (">=2.0.0, <=2.0.0", "<=2.0.0, >=2.0.0", "<=2.0.0, >=2.0.0"),
            (">=0.5.1, <=0.5.1", "<=0.5.1, >=0.5.1", "<=0.5.1, >=0.5.1"),
            (">=10.20.30, <=10.20.30", "<=10.20.30, >=10.20.30", "<=10.20.30, >=10.20.30"),
        ];

        #[test]
        fn singular_interval_orderings_are_equal() {
            for (lower_first, upper_first, _) in SINGULAR {
                let lhs = VersionSpecifiers::from_str(lower_first).unwrap();
                let rhs = VersionSpecifiers::from_str(upper_first).unwrap();
                assert_eq!(
                    lhs, rhs,
                    "specifiers `{lower_first}` and `{upper_first}` should be equal after parse",
                );
            }
        }

        #[test]
        fn singular_interval_normalizes_to_canonical_string() {
            for (lower_first, upper_first, expected) in SINGULAR {
                let lhs = VersionSpecifiers::from_str(lower_first).unwrap();
                let rhs = VersionSpecifiers::from_str(upper_first).unwrap();
                assert_eq!(
                    lhs.to_string(),
                    *expected,
                    "specifier `{lower_first}` should normalize to `{expected}`",
                );
                assert_eq!(
                    rhs.to_string(),
                    *expected,
                    "specifier `{upper_first}` should normalize to `{expected}`",
                );
            }
        }

        #[test]
        fn non_singular_specifiers_unchanged() {
            // Confirm the fix does not disturb the existing primary-by-version
            // ordering when versions differ.
            let s = VersionSpecifiers::from_str(">=1.0, <2.0").unwrap();
            assert_eq!(s.to_string(), ">=1.0, <2.0");
            let s = VersionSpecifiers::from_str("<2.0, >=1.0").unwrap();
            assert_eq!(s.to_string(), ">=1.0, <2.0");
        }
    '''))


def _cleanup_scaffold_test() -> None:
    try:
        SCAFFOLD_TEST.unlink()
    except FileNotFoundError:
        pass


def _run_cargo(*args: str, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["cargo", *args],
        cwd=REPO,
        env=CARGO_ENV,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def setup_module(module):  # noqa: D401
    _write_scaffold_test()


def teardown_module(module):  # noqa: D401
    _cleanup_scaffold_test()


# ─────────── fail_to_pass: behavioral checks (must fail at base) ──────────

def test_singular_interval_orderings_are_equal():
    """`>=X,<=X` and `<=X,>=X` parse to equal VersionSpecifiers."""
    r = _run_cargo(
        "test", "-p", "uv-pep440", "--test", "scaffold_tie_break",
        "--offline", "--quiet", "--",
        "singular_interval_orderings_are_equal", "--exact",
    )
    assert r.returncode == 0, (
        f"singular_interval_orderings_are_equal failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_singular_interval_normalizes_to_canonical_string():
    """The Display impl emits the canonical `<=X, >=X` form for both inputs."""
    r = _run_cargo(
        "test", "-p", "uv-pep440", "--test", "scaffold_tie_break",
        "--offline", "--quiet", "--",
        "singular_interval_normalizes_to_canonical_string", "--exact",
    )
    assert r.returncode == 0, (
        f"singular_interval_normalizes_to_canonical_string failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


# ─────────── pass_to_pass: existing behavior must survive ─────────────────

def test_non_singular_specifiers_unchanged():
    """Distinct-version specifiers still sort by version (no regression)."""
    r = _run_cargo(
        "test", "-p", "uv-pep440", "--test", "scaffold_tie_break",
        "--offline", "--quiet", "--",
        "non_singular_specifiers_unchanged", "--exact",
    )
    assert r.returncode == 0, (
        f"non_singular_specifiers_unchanged failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_uv_pep440_unit_tests_pass():
    """Repo's own uv-pep440 unit tests pass (pass_to_pass)."""
    r = _run_cargo(
        "test", "-p", "uv-pep440", "--lib", "--offline", "--quiet",
        timeout=900,
    )
    assert r.returncode == 0, (
        f"`cargo test -p uv-pep440 --lib` failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_uv_pep440_compiles_clean():
    """`cargo check -p uv-pep440` succeeds (pass_to_pass)."""
    r = _run_cargo(
        "check", "-p", "uv-pep440", "--all-targets", "--offline", "--quiet",
        timeout=600,
    )
    assert r.returncode == 0, (
        f"`cargo check -p uv-pep440` failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )
