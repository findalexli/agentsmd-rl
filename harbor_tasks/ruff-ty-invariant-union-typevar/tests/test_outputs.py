"""
Tests for ruff PR #24698: invariant matching of formal union vs inferable typevar.

Each test calls ty's mdtest harness via `cargo nextest run` and asserts the
relevant markdown fixture passes. The mdtest fixture additions are baked into
the Docker image; the agent's job is to fix `generics.rs` so the new test
cases (which currently fail) start passing.
"""
from __future__ import annotations

import os
import subprocess

REPO = "/workspace/ruff"

# Common nextest command parts. We run with default profile.
NEXTEST_BASE = ["cargo", "nextest", "run", "-p", "ty_python_semantic", "--test", "mdtest"]


def _run(cmd: list[str], *, cwd: str = REPO, timeout: int = 600, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["CARGO_TERM_COLOR"] = "never"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env
    )


def test_constructor_mdtest_passes():
    """fail_to_pass: the constructor.md mdtest fixture passes after the fix.

    At base commit (with the new test cases applied but no code fix), the
    new section "Generic constructor inference from overloaded `__init__`
    self types" fails because the inferable typevar `T` in `ClassSelector[T]`
    is not solved against the union formal `ClassSelector[CT | None]` in
    invariant position. The fix in generics.rs makes the mdtest pass.
    """
    r = _run(NEXTEST_BASE + ["mdtest::call/constructor.md"], timeout=600)
    assert r.returncode == 0, (
        "constructor.md mdtest failed:\n"
        f"--- stdout (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 2000) ---\n{r.stderr[-2000:]}"
    )


def test_overloaded_self_section_passes_with_filter():
    """fail_to_pass: explicitly target the new section via MDTEST_TEST_FILTER.

    Pinning to the section header guards against another constructor.md test
    accidentally masking the signal: if some other test in constructor.md
    breaks but the new section also passes, this still asserts the new
    section's expectations directly.
    """
    r = _run(
        NEXTEST_BASE + ["mdtest::call/constructor.md"],
        env_extra={
            "MDTEST_TEST_FILTER": "Generic constructor inference from overloaded",
        },
        timeout=600,
    )
    assert r.returncode == 0, (
        "Filtered overloaded-self mdtest failed:\n"
        f"--- stdout (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 2000) ---\n{r.stderr[-2000:]}"
    )


def test_generics_legacy_mdtests_pass():
    """pass_to_pass: existing generics/legacy mdtests still pass.

    Guards against fixes that overcorrect and break unrelated generic
    type-inference paths.
    """
    r = _run(NEXTEST_BASE + ["mdtest::generics/legacy"], timeout=900)
    assert r.returncode == 0, (
        "generics/legacy mdtests failed:\n"
        f"--- stdout (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 2000) ---\n{r.stderr[-2000:]}"
    )


def test_ty_python_semantic_compiles():
    """pass_to_pass: the ty_python_semantic crate compiles cleanly.

    A correct fix must not break the build.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr[-3000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_cargo_test_ty_mdtests_github_annotations():
    """pass_to_pass | CI job 'cargo test' -> step 'ty mdtests (GitHub annotations)'

    Runs the mdtest suite via `cargo test` (separate test runner from nextest)
    to ensure the fix works under both test harnesses.
    """
    r = subprocess.run(
        ["bash", "-lc", "cargo test -p ty_python_semantic --test mdtest"],
        cwd=REPO,
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"CI step 'ty mdtests (GitHub annotations)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}"
    )