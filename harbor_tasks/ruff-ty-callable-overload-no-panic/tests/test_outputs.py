"""Tests for astral-sh/ruff#24661 — '[ty] Avoid panicking on overloaded `Callable` type context'.

The bug: when ty's bidirectional type inference encounters a lambda whose target
type context resolves to an overloaded callable (e.g. the `default` parameter
of `dict.get` when the dict's value type is itself a callable), the inference
builder hits an unconditional `panic!()` because it expected a single signature
on the callable.

The fix relaxes that branch to gracefully fall through (no extra type context)
when the callable has more than one overload.

The tests below run the freshly-built `ty` CLI on Python fixtures that trigger
the bug. ty surfaces a Rust panic via:
  - the literal substring 'Panicked at' in its diagnostics output
  - exit code 101
"""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/ruff")
TY_BIN = REPO / "target" / "debug" / "ty"


def _run_ty(source: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Write `source` to a fixture file and invoke `ty check` on it."""
    fixture = tmp_path / "fixture.py"
    fixture.write_text(source)
    assert TY_BIN.exists(), f"ty binary missing at {TY_BIN}"
    return subprocess.run(
        [str(TY_BIN), "check", str(fixture)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )


def _assert_no_panic(result: subprocess.CompletedProcess[str], context: str) -> None:
    combined = (result.stdout or "") + (result.stderr or "")
    lower = combined.lower()
    assert "panicked at" not in lower, (
        f"ty panicked while checking {context}:\n"
        f"  exit code: {result.returncode}\n"
        f"  output (last 800 chars):\n{combined[-800:]}"
    )
    assert "error[panic]" not in lower, (
        f"ty surfaced a panic diagnostic while checking {context}:\n"
        f"  output (last 800 chars):\n{combined[-800:]}"
    )
    assert result.returncode != 101, (
        f"ty exited with the rust panic code (101) while checking {context}:\n"
        f"  output (last 800 chars):\n{combined[-800:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass tests: each triggers the panic on the buggy build.
# ---------------------------------------------------------------------------


def test_dict_get_three_str_methods_lambda_default(tmp_path: Path) -> None:
    """Reproduces the canonical PR fixture: dict whose values are three str
    methods (upper / lower / title), looked up via `.get()` with a lambda
    default. The lambda's target type context resolves to an overloaded
    callable and triggers the panic."""
    src = textwrap.dedent(
        """
        from typing import Callable

        def _(x: bool):
            signatures = {
                "upper": str.upper,
                "lower": str.lower,
                "title": str.title,
            }

            f = signatures.get("", lambda x: x)
            reveal_type(f)
        """
    )
    result = _run_ty(src, tmp_path)
    _assert_no_panic(result, "dict.get with three str-method values")


def test_dict_get_at_module_scope(tmp_path: Path) -> None:
    """Same panic class, but the dict is at module scope rather than inside a
    function — confirms the fix is scope-independent."""
    src = textwrap.dedent(
        """
        signatures = {
            "u": str.upper,
            "l": str.lower,
        }
        result = signatures.get("u", lambda x: x)
        reveal_type(result)
        """
    )
    result = _run_ty(src, tmp_path)
    _assert_no_panic(result, "module-scope dict.get with two str-method values")


def test_dict_setdefault_with_lambda(tmp_path: Path) -> None:
    """dict.setdefault is overloaded just like dict.get, so passing a lambda
    as the default also hit the same panic on the buggy build."""
    src = textwrap.dedent(
        """
        sigs = {
            "u": str.upper,
            "l": str.lower,
            "t": str.title,
        }
        sigs.setdefault("u", lambda x: x)
        """
    )
    result = _run_ty(src, tmp_path)
    _assert_no_panic(result, "dict.setdefault with str-method values")


def test_dict_get_single_str_method_value(tmp_path: Path) -> None:
    """Even a dict with a single str-method value triggers the panic, because
    dict.get's own overloads make the lambda's target type context
    overloaded."""
    src = textwrap.dedent(
        """
        sigs = {"u": str.upper}
        sigs.get("u", lambda x: x)
        """
    )
    result = _run_ty(src, tmp_path)
    _assert_no_panic(result, "dict.get with a single str-method value")


# ---------------------------------------------------------------------------
# Pass-to-pass tests: workspace builds & runs successfully on base + fix.
# ---------------------------------------------------------------------------


def test_ty_python_semantic_compiles() -> None:
    """The targeted crate must still compile cleanly after the fix."""
    result = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        "cargo check failed for ty_python_semantic:\n" + result.stderr[-2000:]
    )


def test_ty_binary_runs_smoke() -> None:
    """Smoke test: the `ty` binary launches and reports its version."""
    result = subprocess.run(
        [str(TY_BIN), "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"ty --version failed: {result.stderr}"
    assert "ruff" in (result.stdout + result.stderr).lower() or \
           "ty" in (result.stdout + result.stderr).lower(), (
        f"unexpected version output: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_ty_check_clean_python_file(tmp_path: Path) -> None:
    """Sanity: `ty check` on a benign Python file does not panic and exits
    successfully (no diagnostics expected)."""
    fixture = tmp_path / "ok.py"
    fixture.write_text("x: int = 1\n")
    result = subprocess.run(
        [str(TY_BIN), "check", str(fixture)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert "panicked" not in combined.lower(), (
        f"ty panicked on a trivial file: {combined[-500:]}"
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