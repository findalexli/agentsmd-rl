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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_scripts_python():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_ast/generate.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_python_2():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_formatter/generate.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_scripts_add_rule_py():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/add_rule.py --name DoTheThing --prefix F --code 999 --linter pyflakes'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_cargo():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_scripts_add_plugin_py():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/add_plugin.py test --url https://pypi.org/project/-test/0.1.0/ --prefix TST && ./scripts/add_rule.py --name FirstRule --prefix TST --code 001 --linter test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_uv():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --directory=./python/py-fuzzer mypy'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_uv_2():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --directory=./python/py-fuzzer ruff format --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_uv_3():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --directory=./python/py-fuzzer ruff check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_ty_mdtests_github_annotations():
    """pass_to_pass | CI job 'cargo test' → step 'ty mdtests (GitHub annotations)'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test -p ty_python_semantic --test mdtest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'ty mdtests (GitHub annotations)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_run_tests():
    """pass_to_pass | CI job 'cargo test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo insta test --all-features --unreferenced reject --test-runner nextest --disable-nextest-doctest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_run_doctests():
    """pass_to_pass | CI job 'cargo test' → step 'Run doctests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test --doc --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run doctests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")