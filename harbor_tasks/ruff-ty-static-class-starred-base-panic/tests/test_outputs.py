"""Behavioural tests for the per-base lint panic fix in ty.

We verify that running ``ty check`` on Python files that contain class
definitions whose bases include a starred *fixed-length* tuple does not
panic, and that the appropriate per-base diagnostics are emitted.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/ruff")
TY_BIN = REPO / "target" / "debug" / "ty"


def _ty_check(source: str, *, filename: str = "case.py") -> subprocess.CompletedProcess[str]:
    """Run the freshly built ``ty`` binary on a temporary file and return the
    completed process.  Output formatting is forced to ``concise`` so the
    diagnostic strings we check against are stable."""
    workdir = Path("/tmp") / f"ty_case_{os.getpid()}_{abs(hash(source)) % 10**8}"
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    src = workdir / filename
    src.write_text(textwrap.dedent(source))
    proc = subprocess.run(
        [str(TY_BIN), "check", "--output-format", "concise", str(src)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(workdir),
        env={**os.environ, "RUST_BACKTRACE": "0", "NO_COLOR": "1"},
    )
    return proc


def _assert_no_panic(proc: subprocess.CompletedProcess[str]) -> None:
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert "panicked at" not in combined, (
        f"ty panicked.\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )
    # A Rust panic with the default abort handler exits with code 101.
    assert proc.returncode != 101, (
        f"ty exited with 101 (Rust panic).\n--- stdout ---\n{proc.stdout}"
        f"\n--- stderr ---\n{proc.stderr}"
    )


# ───────────────────────────── fail-to-pass ───────────────────────────────
# These tests must FAIL on the buggy base commit (ty either panics outright,
# or — depending on which final-class lookup happens first — emits no
# diagnostic on the unpacked entries) and PASS once the fix is applied.

def test_inherits_from_final_via_starred_tuple_no_panic() -> None:
    """Inheriting a final class through a starred fixed-length tuple
    literal must not panic and must report subclass-of-final-class."""
    proc = _ty_check(
        """
        class InheritsFromFinalViaStarred(*(int, bool)): ...
        """
    )
    _assert_no_panic(proc)
    out = proc.stdout + proc.stderr
    assert "subclass-of-final-class" in out, (
        f"missing subclass-of-final-class diagnostic.\n{out}"
    )


def test_inherits_from_final_via_named_starred_tuple_no_panic() -> None:
    """Same as above but the tuple is bound to a name first."""
    proc = _ty_check(
        """
        final_bases = (int, bool)
        class InheritsFromFinalViaNamedStarred(*final_bases): ...
        """
    )
    _assert_no_panic(proc)
    out = proc.stdout + proc.stderr
    assert "subclass-of-final-class" in out, (
        f"missing subclass-of-final-class diagnostic.\n{out}"
    )


def test_named_tuple_with_starred_bases_emits_invalid_named_tuple() -> None:
    """A NamedTuple class with extra starred bases must report
    invalid-named-tuple for each unpacked extra base, not panic."""
    proc = _ty_check(
        """
        from typing import NamedTuple
        class NamedTupleWithStarredBases(NamedTuple, *(int, str)): ...
        """
    )
    _assert_no_panic(proc)
    out = proc.stdout + proc.stderr
    # The patch's expected diagnostics for the unpacked entries.
    assert "invalid-named-tuple" in out, (
        f"missing invalid-named-tuple diagnostic.\n{out}"
    )


def test_protocol_with_starred_bases_emits_invalid_protocol() -> None:
    """A Protocol class with starred non-protocol bases must emit
    invalid-protocol diagnostics for the unpacked entries, not panic."""
    proc = _ty_check(
        """
        from typing import Protocol
        class ProtocolWithStarredBases(Protocol, *(int, str)): ...
        """
    )
    _assert_no_panic(proc)
    out = proc.stdout + proc.stderr
    assert "invalid-protocol" in out, (
        f"missing invalid-protocol diagnostic.\n{out}"
    )


def test_bare_generic_in_starred_tuple_emits_invalid_base() -> None:
    """A bare ``Generic`` reached through a starred tuple base must produce
    the invalid-base diagnostic without panicking."""
    proc = _ty_check(
        """
        from typing import Generic
        class BareGenericInStarred(*(int, Generic)): ...
        """
    )
    _assert_no_panic(proc)
    out = proc.stdout + proc.stderr
    assert "invalid-base" in out, f"missing invalid-base diagnostic.\n{out}"


# ───────────────────────────── pass-to-pass ───────────────────────────────
# These tests must PASS on both the base commit and the fixed commit.

def test_ty_binary_present() -> None:
    """The build step in test.sh must have produced the ty binary."""
    assert TY_BIN.exists(), f"missing ty binary: {TY_BIN}"


def test_plain_class_no_diagnostics() -> None:
    """A vanilla, non-panic class definition must remain diagnostic-free.
    Guards against the fix accidentally over-firing on normal code."""
    proc = _ty_check(
        """
        class A: ...
        class B(A): ...
        """
    )
    _assert_no_panic(proc)
    assert proc.returncode == 0, (
        f"plain class definitions should not produce diagnostics.\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_subclass_of_final_class_without_starred_tuple() -> None:
    """The pre-existing, non-starred subclass-of-final-class diagnostic must
    still fire after the refactor — guard against regressions in the path
    that the patch refactors heavily."""
    proc = _ty_check(
        """
        class FinalChild(bool): ...
        """
    )
    _assert_no_panic(proc)
    out = proc.stdout + proc.stderr
    assert "subclass-of-final-class" in out, (
        f"regression: subclass-of-final-class no longer fires for plain "
        f"inheritance from a final class.\n{out}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_cargo_test_dogfood_ty_on_py_fuzzer():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on py-fuzzer'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./python/py-fuzzer cargo run -p ty check --project=./python/py-fuzzer'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on py-fuzzer' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_the_scripts_directory():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on the scripts directory'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./scripts cargo run -p ty check --project=./scripts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on the scripts directory' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_ty_benchmark():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on ty_benchmark'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./scripts/ty_benchmark cargo run -p ty check --project=./scripts/ty_benchmark'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on ty_benchmark' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_cargo():
    """pass_to_pass | CI job 'cargo test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo doc --all --no-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_cargo_2():
    """pass_to_pass | CI job 'cargo test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo doc --no-deps -p ty_python_semantic -p ty_python_core -p ty_module_resolver -p ty_site_packages -p ty_combine -p ty_project -p ty_ide -p ty_wasm -p ty_vendored -p ty_static -p ty -p ty_test -p ruff_db -p ruff_python_formatter --document-private-items'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_ruff_lsp_build_ruff_binary():
    """pass_to_pass | CI job 'test ruff-lsp' → step 'Build Ruff binary'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build -p ruff --bin ruff'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Ruff binary' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_ruff_lsp_run_ruff_lsp_tests():
    """pass_to_pass | CI job 'test ruff-lsp' → step 'Run ruff-lsp tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip uninstall --yes ruff && ruff version && just test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run ruff-lsp tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_build_build_tests():
    """pass_to_pass | CI job 'cargo build' → step 'Build tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo "+${MSRV}" test --no-run --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")