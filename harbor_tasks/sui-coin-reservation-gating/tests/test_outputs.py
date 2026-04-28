"""Tests for Sui coin reservation protocol config gating fix.

This PR adds protocol config gating to prevent fake coins from being returned
when coin reservations are disabled in the protocol configuration.
"""

import subprocess
import re
import os

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-json-rpc/src/authority_state.rs"


def test_cargo_check():
    """Verify code compiles successfully (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-json-rpc"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_get_object_read_has_protocol_gating():
    """Verify get_object_read checks enable_coin_reservation_obj_refs() before returning fake coins.

    The fix adds a protocol config check in get_object_read() to only return fake coins
    when coin reservations are enabled. This test checks that the gating logic exists.
    """
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the get_object_read function
    func_match = re.search(
        r'fn get_object_read\(&self, object_id: &ObjectID\) -> StateReadResult<ObjectRead>\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        content,
        re.DOTALL
    )
    assert func_match, "Could not find get_object_read function"

    func_body = func_match.group(1)

    # Check for the protocol config gating - the fix adds this check
    assert "enable_coin_reservation_obj_refs()" in func_body, \
        "get_object_read must check enable_coin_reservation_obj_refs() before returning fake coins"

    # Verify the check is in the right context - it should be in the NotExists branch
    notexists_pattern = r'if let ObjectRead::NotExists\([^)]+\)\s*= result.*?&&.*?enable_coin_reservation_obj_refs\(\)'
    assert re.search(notexists_pattern, func_body, re.DOTALL), \
        "enable_coin_reservation_obj_refs() check must be combined with ObjectRead::NotExists check"


def test_get_owned_coins_has_protocol_gating():
    """Verify get_owned_coins checks enable_coin_reservation_obj_refs() before building fake coins.

    The fix adds a protocol config check in get_owned_coins() to only build fake coins
    when coin reservations are enabled. This test checks that the gating logic exists.
    """
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the get_owned_coins function - it's a large function
    # Look for the pattern that indicates the start of the function
    func_match = re.search(
        r'fn get_owned_coins.*?\{',
        content,
        re.DOTALL
    )
    assert func_match, "Could not find get_owned_coins function start"

    # Find the coin_reservations_enabled variable assignment - this is the key fix
    assert "coin_reservations_enabled" in content, \
        "get_owned_coins must define coin_reservations_enabled variable"

    assert "enable_coin_reservation_obj_refs()" in content, \
        "get_owned_coins must check enable_coin_reservation_obj_refs()"

    # Verify the logic: if !coin_reservations_enabled { HashMap::new() }
    gating_pattern = r'if !coin_reservations_enabled\s*\{\s*HashMap::new\(\)'
    assert re.search(gating_pattern, content, re.DOTALL), \
        "Must return empty HashMap when coin_reservations_enabled is false"


def test_cargo_fmt():
    """Verify code formatting passes (pass_to_pass).

    This runs cargo fmt check which is part of CI linting.
    """
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo fmt check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_cargo_clippy_package():
    """Verify clippy passes on sui-json-rpc package (pass_to_pass).

    This runs clippy on the modified package with warnings as errors.
    """
    result = subprocess.run(
        ["cargo", "clippy", "--package", "sui-json-rpc", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo clippy failed:\n{result.stderr[-1000:]}"


def test_git_checks():
    """Verify git repo checks pass (pass_to_pass).

    This runs the repo's standard git checks script used in CI.
    """
    result = subprocess.run(
        ["bash", "scripts/git-checks.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"git-checks.sh failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_external_crates_test_external_crates_tests():
    """pass_to_pass | CI job 'external-crates-test' → step 'External crates tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo xtest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'External crates tests' failed (returncode={r.returncode}):\n"
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

def test_ci_move_formatter___run_tests_npm():
    """pass_to_pass | CI job 'Move Formatter - run tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm i && npm test'], cwd=os.path.join(REPO, 'external-crates/move/tooling/prettier-move'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint__build__and_test_build():
    """pass_to_pass | CI job 'Lint, Build, and Test' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=os.path.join(REPO, './docs/site'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
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

def test_ci_check_docs_run_afdocs_check():
    """pass_to_pass | CI job 'check-docs' → step 'Run afdocs check'"""
    r = subprocess.run(
        ["bash", "-lc", 'OUTPUT=$(npx --yes afdocs@0.6.0 check "$URL" --max-links 1000 2>&1) || true\necho "result<<EOF" >> $GITHUB_OUTPUT\necho "$OUTPUT" >> $GITHUB_OUTPUT\necho "EOF" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run afdocs check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")