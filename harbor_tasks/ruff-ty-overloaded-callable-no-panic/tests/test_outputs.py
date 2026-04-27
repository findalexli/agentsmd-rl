"""Tests for ruff PR #24661 — avoid panic on overloaded Callable type context."""

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/ruff")
MDTEST_DIR = REPO / "crates" / "ty_python_semantic" / "resources" / "mdtest"
REGRESSION_NAME = "regression_pr24661.md"
REGRESSION_PATH = MDTEST_DIR / REGRESSION_NAME

REGRESSION_CONTENT = """\
# Regression test for PR #24661

Calling `dict.get` (an overloaded callable, three overloads in typeshed)
with a `lambda` for the `default` parameter used to crash the type
checker. The expected-type machinery dispatched to a code path that
asserted the inferred `Callable` type-context was non-overloaded; with
`dict.get` it always is, which fired a hard `panic!` in
`crates/ty_python_semantic/src/types/infer/builder.rs`. The well-formed
behaviour is to return without panicking — exact return-type details for
the lambda are not checked here.

```py
def _(x: bool):
    signatures = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
    }
    f = signatures.get("", lambda x: x)
```
"""


def _cargo_env() -> dict[str, str]:
    env = os.environ.copy()
    env["CARGO_PROFILE_DEV_OPT_LEVEL"] = "1"
    env["INSTA_FORCE_PASS"] = "1"
    env["INSTA_UPDATE"] = "always"
    env["CARGO_TERM_COLOR"] = "never"
    return env


def _ensure_regression_file() -> None:
    REGRESSION_PATH.write_text(REGRESSION_CONTENT)


def _run_mdtest(filter_str: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "cargo",
            "nextest",
            "run",
            "--locked",
            "-p",
            "ty_python_semantic",
            "--test",
            "mdtest",
            "--",
            filter_str,
        ],
        cwd=str(REPO),
        env=_cargo_env(),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_overloaded_callable_does_not_panic():
    """fail_to_pass: calling dict.get with a lambda default must not crash ty."""
    _ensure_regression_file()
    r = _run_mdtest("mdtest::regression_pr24661")
    output = r.stdout + "\n" + r.stderr
    assert r.returncode == 0, (
        "ty type checker crashed (or mdtest failed) on the regression input:\n"
        f"--- STDOUT (last 2000 chars) ---\n{r.stdout[-2000:]}\n"
        f"--- STDERR (last 2000 chars) ---\n{r.stderr[-2000:]}"
    )
    assert "1 passed" in output, (
        "regression mdtest was not actually executed/recognised — datatest_stable "
        "did not pick up the new fixture file:\n"
        f"--- STDOUT ---\n{r.stdout[-2000:]}\n--- STDERR ---\n{r.stderr[-2000:]}"
    )


def test_bidirectional_mdtest_pass_to_pass():
    """pass_to_pass: pre-existing bidirectional.md mdtest still passes."""
    r = _run_mdtest("mdtest::bidirectional", timeout=600)
    assert r.returncode == 0, (
        "pre-existing bidirectional.md mdtest regressed:\n"
        f"--- STDOUT ---\n{r.stdout[-2000:]}\n--- STDERR ---\n{r.stderr[-2000:]}"
    )


def test_ty_python_semantic_compiles():
    """pass_to_pass: ty_python_semantic crate compiles cleanly."""
    r = subprocess.run(
        [
            "cargo",
            "check",
            "--locked",
            "-p",
            "ty_python_semantic",
            "--tests",
        ],
        cwd=str(REPO),
        env=_cargo_env(),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr[-2000:]}"
    )
