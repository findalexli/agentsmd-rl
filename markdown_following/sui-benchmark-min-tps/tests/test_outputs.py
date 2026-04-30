"""Test file for sui-benchmark --min-tps feature."""

import subprocess
import os

REPO = "/workspace/sui"


# ============================================================================
# Fail-to-Pass Tests
# ============================================================================


def test_min_tps_compiles():
    """The min_tps code compiles successfully with cargo check."""
    r = subprocess.run(
        ["cargo", "check", "--package", "sui-benchmark"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_min_tps_option_parses():
    """The stress binary has --min-tps option defined on the Opts struct."""
    opts_path = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    with open(opts_path) as f:
        content = f.read()

    assert "pub min_tps: Option<f64>" in content, (
        "min_tps field with type Option<f64> not found in Opts struct")
    assert '#[clap(long, global = true)]' in content, (
        "min_tps clap attribute '#[clap(long, global = true)]' missing")
    content_lower = content.lower()
    assert ("minimum threshold" in content_lower
            or "below this threshold" in content_lower
            or "threshold" in content_lower), (
        "min_tps doc comment about minimum threshold not found")


def test_min_tps_validation_in_stress():
    """min_tps validation logic exists in stress.rs with TPS calculation and error handling."""
    stress_path = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")
    with open(stress_path) as f:
        content = f.read()

    assert "let min_tps = opts.min_tps;" in content, (
        "min_tps extraction 'let min_tps = opts.min_tps;' not found")
    assert "if let Some(min_tps) = min_tps" in content, (
        "min_tps validation block 'if let Some(min_tps) = min_tps' not found")
    assert "num_success_txes as f64" in content, (
        "num_success_txes TPS calculation not found")
    assert "duration.as_secs_f64()" in content, (
        "duration.as_secs_f64() TPS calculation not found")
    assert "is below minimum threshold" in content, (
        "TPS below threshold error message not found")
    assert "anyhow::anyhow!" in content or "anyhow!(" in content, (
        "anyhow error macro not found for TPS failure")


# ============================================================================
# Pass-to-Pass Tests
# ============================================================================


def test_license_header_options_rs():
    """options.rs has required Apache-2.0 license header."""
    opts_path = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    with open(opts_path) as f:
        content = f.read()

    assert "SPDX-License-Identifier: Apache-2.0" in content, (
        "Apache-2.0 license header missing in options.rs")
    assert "Copyright (c) Mysten Labs, Inc." in content, (
        "Copyright header missing in options.rs")


def test_license_header_stress_rs():
    """stress.rs has required Apache-2.0 license header."""
    stress_path = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")
    with open(stress_path) as f:
        content = f.read()

    assert "SPDX-License-Identifier: Apache-2.0" in content, (
        "Apache-2.0 license header missing in stress.rs")
    assert "Copyright (c) Mysten Labs, Inc." in content, (
        "Copyright header missing in stress.rs")


def test_repo_cargo_fmt():
    """Repo code passes cargo fmt --check linting."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


def test_repo_git_checks():
    """Repo passes git sanity checks (no submodules, bad filenames, whitespace)."""
    r = subprocess.run(
        ["./scripts/git-checks.sh"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git-checks.sh failed:\n{r.stderr[-500:]}"


def test_repo_xlint():
    """Repo passes cargo xlint license check."""
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo xlint failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_external_crates_test_external_crates_tests():
    """pass_to_pass | CI job 'external-crates-test' → step 'External crates tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo xtest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'External crates tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_move_formatter___run_tests_npm():
    """pass_to_pass | CI job 'Move Formatter - run tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm i && npm test'], cwd=os.path.join(REPO, 'external-crates/move/tooling/prettier-move'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tree_sitter___run_tests_run_tests_sh():
    """pass_to_pass | CI job 'Tree Sitter - run tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './run-tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_move_formatter___check_formatt_npx():
    """pass_to_pass | CI job 'Move Formatter - check formatting' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx prettier-move -c **/*.move'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint__build__and_test_manypkg_check():
    """pass_to_pass | CI job 'Lint, Build, and Test' → step 'Manypkg Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm manypkg check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Manypkg Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint__build__and_test_lint():
    """pass_to_pass | CI job 'Lint, Build, and Test' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm turbo lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint__build__and_test_build():
    """pass_to_pass | CI job 'Lint, Build, and Test' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm turbo build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint__build__and_test_test():
    """pass_to_pass | CI job 'Lint, Build, and Test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_cargo_test():
    """pass_to_pass | CI job 'test' → step 'cargo test'"""
    r = subprocess.run(
        ["bash", "-lc", "cargo nextest run --profile ci --cargo-quiet -E 'package(sui-bridge) | package(sui-bridge-indexer)'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'cargo test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_license_check_run_license_check():
    """pass_to_pass | CI job 'license-check' → step 'Run license check'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo xlint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run license check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_windows_cli_tests_cargo_test():
    """pass_to_pass | CI job 'windows-cli-tests' → step 'cargo test'"""
    r = subprocess.run(
        ["bash", "-lc", "cargo nextest run --profile ci --cargo-quiet -E '!package(sui-bridge) and !package(sui-bridge-indexer)'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'cargo test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_windows_build_cargo_build():
    """pass_to_pass | CI job 'windows-build' → step 'cargo build'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'cargo build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")