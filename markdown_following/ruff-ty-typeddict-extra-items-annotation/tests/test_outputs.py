"""
Task: ruff-ty-typeddict-extra-items-annotation
Repo: ruff @ a617c54b0708a8c1eb850cc3b2a5caee21137a28
PR:   24362

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"


def _build_ty():
    """Build the ty binary (idempotent — skips if already built)."""
    ty = Path(REPO, "target", "debug", "ty")
    if ty.exists():
        return str(ty)
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO, capture_output=True, timeout=900, env=env,
    )
    assert r.returncode == 0, f"ty build failed:\n{r.stderr.decode()[-3000:]}"
    return str(ty)


def _ty_check(code, suffix=".py"):
    """Run ty check on a Python code snippet, return combined stdout+stderr."""
    ty = _build_ty()
    fd, path = tempfile.mkstemp(suffix=suffix, dir=REPO)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run(
            [ty, "check", path],
            cwd=REPO, capture_output=True, timeout=120,
        )
        return r.stdout.decode() + "\n" + r.stderr.decode()
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate compiles without errors (pass_to_pass)."""
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, timeout=900, env=env,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-3000:]}"


# [repo_tests] pass_to_pass — ty binary smoke test
def test_ty_check_smoke():
    """ty binary can check a simple Python file without crashing (pass_to_pass)."""
    ty = _build_ty()
    fd, path = tempfile.mkstemp(suffix=".py", dir=REPO)
    try:
        with os.fdopen(fd, "w") as f:
            f.write("x: int = 1\n")
        r = subprocess.run(
            [ty, "check", path],
            cwd=REPO, capture_output=True, timeout=120,
        )
        # ty check should succeed on valid code (exit code 0)
        assert r.returncode == 0, f"ty check failed:\n{r.stderr.decode()[-1000:]}"
    finally:
        os.unlink(path)


# [repo_tests] pass_to_pass — repo's CI unit tests for ty_python_semantic (subset for speed)
def test_ty_python_semantic_unit_tests():
    """ty_python_semantic unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--", "types::typed_dict"],
        cwd=REPO, capture_output=True, timeout=180,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr.decode()[-2000:]}"


# [repo_tests] pass_to_pass — repo's TypedDict mdtest
def test_ty_python_semantic_typed_dict_mdtest():
    """ty_python_semantic TypedDict mdtest passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest", "--", "typed_dict"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"TypedDict mdtest failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_required_rejected_in_extra_items():
    """ty reports invalid-type-form when Required is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, Required\n"
        "\n"
        "class TD1(TypedDict, extra_items=Required[int]):\n"
        "    name: str\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for Required in extra_items, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_not_required_rejected_in_extra_items():
    """ty reports invalid-type-form when NotRequired is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, NotRequired\n"
        "\n"
        "class TD2(TypedDict, extra_items=NotRequired[str]):\n"
        "    x: int\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for NotRequired in extra_items, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_classvar_rejected_in_extra_items():
    """ty reports invalid-type-form when ClassVar is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, ClassVar\n"
        "\n"
        "class TD3(TypedDict, extra_items=ClassVar[int]):\n"
        "    label: str\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for ClassVar in extra_items, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_final_rejected_in_extra_items():
    """ty reports invalid-type-form when Final is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, Final\n"
        "\n"
        "class TD4(TypedDict, extra_items=Final[int]):\n"
        "    key: str\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for Final in extra_items, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — valid extra_items must still be accepted
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_readonly_extra_items_accepted():
    """ty does NOT report invalid-type-form for ReadOnly or plain types in extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, ReadOnly\n"
        "\n"
        "class Good1(TypedDict, extra_items=int):\n"
        "    name: str\n"
        "\n"
        "class Good2(TypedDict, extra_items=ReadOnly[int]):\n"
        "    name: str\n"
    )
    assert "invalid-type-form" not in output, (
        f"Unexpected invalid-type-form error for valid extra_items:\n{output}"
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

def test_ci_benchmarks_instrumented_ty_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks instrumented ty' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m simulation -m memory --features "codspeed,ty_instrumented" --profile profiling --no-default-features -p ruff_benchmark --bench ty'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_build_build_tests():
    """pass_to_pass | CI job 'cargo build' → step 'Build tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo "+${MSRV}" test --no-run --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build tests' failed (returncode={r.returncode}):\n"
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
        ["bash", "-lc", 'cargo insta test --all-features --unreferenced reject --test-runner nextest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")