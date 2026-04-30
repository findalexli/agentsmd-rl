"""Verifies the noShadow rule correctly handles destructuring patterns.

Fail-to-pass tests: the base commit emits wrong diagnostics (or none) for
destructuring patterns; the gold fix walks through binding-pattern declarations
and handles them correctly.

Pass-to-pass tests: existing fixtures must not regress, and repo-level CI
checks (fmt, cargo check, rules validation) must stay green.
"""
import subprocess
from pathlib import Path

REPO = Path("/workspace/biome")


def _cargo_test(filter_arg: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["cargo", "test", "-p", "biome_js_analyze", "--test", "spec_tests", "--", "--exact", filter_arg],
        cwd=REPO, capture_output=True, text=True, timeout=timeout,
    )


# ====== fail_to_pass ======

def test_valid_destructuring_not_flagged():
    """Base: rule treats destructured bindings in sibling scopes as shadows,
    emitting false-positive diagnostics. The validDestructuring.js snapshot
    expects no diagnostics -> mismatch -> insta panic.
    Gold: no diagnostics, snapshot matches."""
    r = _cargo_test("specs::nursery::no_shadow::valid_destructuring_js")
    assert r.returncode == 0, (
        f"validDestructuring spec failed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )
    assert "1 passed" in r.stdout or "test result: ok" in r.stdout


def test_all_no_shadow_snapshot_tests_pass():
    """Base: the noShadow snapshot suite fails because validDestructuring.js
    emits false positives. Gold: all 5 fixtures (invalid.js, valid.js,
    valid-func-in-type.ts, invalidDestructuring.js, validDestructuring.js)
    pass."""
    r = subprocess.run(
        ["bash", "-lc", "cargo test -p biome_js_analyze --test spec_tests -- nursery::no_shadow"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"noShadow snapshot suite failed:\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )


# ====== pass_to_pass ======

def test_invalid_destructuring_detected():
    """The invalidDestructuring.js snapshot expects 7 noShadow diagnostics for
    destructured shadowed bindings. Both base (via its default-true path) and
    gold (via correct declaration recognition) produce diagnostics matching
    the snapshot."""
    r = _cargo_test("specs::nursery::no_shadow::invalid_destructuring_js")
    assert r.returncode == 0, (
        f"invalidDestructuring spec failed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )
    assert "1 passed" in r.stdout or "test result: ok" in r.stdout


def test_existing_no_shadow_invalid_still_passes():
    """The original invalid.js fixture must still detect shadows."""
    r = _cargo_test("specs::nursery::no_shadow::invalid_js")
    assert r.returncode == 0, (
        f"existing noShadow/invalid.js regressed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_existing_no_shadow_valid_still_passes():
    """The original valid.js fixture must remain quiet."""
    r = _cargo_test("specs::nursery::no_shadow::valid_js")
    assert r.returncode == 0, (
        f"existing noShadow/valid.js regressed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_existing_no_shadow_valid_func_in_type_still_passes():
    """The TypeScript valid-func-in-type.ts fixture must remain quiet."""
    r = _cargo_test("specs::nursery::no_shadow::valid_func_in_type_ts")
    assert r.returncode == 0, (
        f"existing noShadow/valid-func-in-type.ts regressed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )


# ====== CI-mined pass_to_pass ======

def test_ci_format_rust_files_run_rustfmt():
    """CI 'Format Rust Files' — rustfmt must be clean across the workspace."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"rustfmt check failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_dependencies_run_udeps():
    """pass_to_pass | CI job 'Check Dependencies' → step 'Run udeps'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo +nightly udeps --all-targets'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run udeps' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_rust_files_run_cargo_check():
    """pass_to_pass | CI job 'Lint Rust Files' → step 'Run cargo check'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo check --workspace --all-targets --release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run cargo check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_rust_files_run_clippy():
    """pass_to_pass | CI job 'Lint Rust Files' → step 'Run clippy'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clippy' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests_on_matrix_os():
    """pass_to_pass | CI job 'Test' → step 'Run tests on ${{ matrix.os }}'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test --workspace --features=js_plugin'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests on ${{ matrix.os }}' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_rust_files_format_toml_files():
    """pass_to_pass | CI job 'Format Rust Files' → step 'Format TOML files'"""
    r = subprocess.run(
        ["bash", "-lc", 'tombi format --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format TOML files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_rules_documentation_run_rules_check():
    """pass_to_pass | CI job 'Validate rules documentation' → step 'Run rules check'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo run -p rules_check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run rules check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
