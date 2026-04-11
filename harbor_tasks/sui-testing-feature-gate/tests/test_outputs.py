"""Tests for the testing feature gate task.

This verifies that the PR correctly replaces #[cfg(debug_assertions)] with #[cfg(feature = "testing")]
for test-only code that needs to be callable cross-crate.
"""

import subprocess
import re

REPO = "/workspace/sui"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks that must pass on both base and fix)
# =============================================================================

def test_repo_rustfmt_check():
    """Repo code must be properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Rustfmt check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_cargo_check_sui_types():
    """cargo check -p sui-types must pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-types"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check sui-types failed:\n{r.stderr[-500:]}"


def test_sui_types_testing_feature_defined():
    """sui-types Cargo.toml must have testing = [] feature defined (origin: static)."""
    cargo_toml = f"{REPO}/crates/sui-types/Cargo.toml"
    with open(cargo_toml) as f:
        content = f.read()

    # Check that testing feature is defined
    assert 'testing = []' in content, "sui-types must define testing = [] feature"


def test_sui_types_gasless_functions_use_testing_gate():
    """Gasless token testing functions must use #[cfg(feature = "testing")] (origin: static)."""
    transaction_rs = f"{REPO}/crates/sui-types/src/transaction.rs"
    with open(transaction_rs) as f:
        content = f.read()

    # Check that key functions use testing feature gate
    assert '#[cfg(feature = "testing")]' in content, "Must use #[cfg(feature = \"testing\")] for test-only code"

    # Verify the specific functions are gated
    assert "static GASLESS_TOKENS_FOR_TESTING" in content
    assert "pub fn add_gasless_token_for_testing" in content
    assert "pub fn clear_gasless_tokens_for_testing" in content


def test_apply_test_token_uses_testing_gate():
    """apply_test_token_overrides must use #[cfg(feature = "testing")] (origin: static)."""
    transaction_rs = f"{REPO}/crates/sui-types/src/transaction.rs"
    with open(transaction_rs) as f:
        content = f.read()

    # Check that apply_test_token_overrides uses testing gate
    # It should NOT use debug_assertions anymore
    pattern = r'fn apply_test_token_overrides.*?#\[cfg\(feature = "testing"\)\]'
    match = re.search(pattern, content, re.DOTALL)

    # Also verify debug_assertions is not used for this purpose
    assert '#[cfg(debug_assertions)]' not in content, "Must not use debug_assertions for test-only code"


def test_transactional_test_runner_testing_feature():
    """sui-transactional-test-runner must have testing feature defined (origin: static)."""
    cargo_toml = f"{REPO}/crates/sui-transactional-test-runner/Cargo.toml"
    with open(cargo_toml) as f:
        content = f.read()

    # Check that testing feature exists and depends on sui-types/testing
    assert '[features]' in content
    assert 'testing = ["sui-types/testing"]' in content

    # Check that the binary requires the testing feature
    assert '[[bin]]' in content
    assert 'required-features = ["testing"]' in content


def test_transactional_test_runner_lib_gated():
    """sui-transactional-test-runner lib.rs must use #[cfg(feature = "testing")] (origin: static)."""
    lib_rs = f"{REPO}/crates/sui-transactional-test-runner/src/lib.rs"
    with open(lib_rs) as f:
        content = f.read()

    # Count occurrences of #[cfg(feature = "testing")] - should be many
    testing_gates = content.count('#[cfg(feature = "testing")]')
    assert testing_gates >= 10, f"Expected at least 10 testing feature gates, found {testing_gates}"


def test_transactional_test_runner_no_debug_assertions():
    """sui-transactional-test-runner must not use debug_assertions for gating (origin: static)."""
    lib_rs = f"{REPO}/crates/sui-transactional-test-runner/src/lib.rs"
    with open(lib_rs) as f:
        content = f.read()

    assert '#[cfg(debug_assertions)]' not in content, "Must not use debug_assertions in lib.rs"


def test_transactional_test_runner_test_adapter():
    """test_adapter.rs must call gasless functions without debug_assertions check (origin: static)."""
    test_adapter_rs = f"{REPO}/crates/sui-transactional-test-runner/src/test_adapter.rs"
    with open(test_adapter_rs) as f:
        content = f.read()

    # The call to clear_gasless_tokens_for_testing should NOT be gated by debug_assertions
    assert '#[cfg(debug_assertions)]' not in content, "test_adapter.rs must not use debug_assertions"

    # The gasless functions should be called directly
    assert "clear_gasless_tokens_for_testing()" in content
    assert "add_gasless_token_for_testing(" in content


def test_upstream_crates_enable_testing_feature():
    """Upstream test crates must enable testing feature via dev-dependencies (origin: static)."""

    crates_to_check = [
        "crates/sui-adapter-transactional-tests/Cargo.toml",
        "crates/sui-verifier-transactional-tests/Cargo.toml",
        "crates/sui-indexer-alt-e2e-tests/Cargo.toml",
    ]

    for crate_path in crates_to_check:
        cargo_toml = f"{REPO}/{crate_path}"
        with open(cargo_toml) as f:
            content = f.read()

        # Must have features = ["testing"] in sui-transactional-test-runner dependency
        pattern = r'sui-transactional-test-runner\s*=\s*\{[^}]*features\s*=\s*\[\s*"testing"\s*\][^}]*\}'
        match = re.search(pattern, content, re.DOTALL)
        assert match is not None, f"{crate_path} must enable testing feature for sui-transactional-test-runner"


def test_repo_cargo_clippy_sui_types():
    """cargo clippy -p sui-types must pass (pass_to_pass / origin: repo_tests)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-types", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


def test_repo_cargo_xlint():
    """cargo xlint must pass (pass_to_pass / origin: repo_tests)."""
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo xlint failed:\n{r.stderr[-500:]}"


def test_cargo_check_sui_types_release():
    """cargo check --release -p sui-types must pass (pass_to_pass / origin: repo_tests)."""
    result = subprocess.run(
        ["cargo", "check", "--release", "-p", "sui-types"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )

    assert result.returncode == 0, f"cargo check --release -p sui-types failed:\n{result.stderr.decode()}"


def test_cargo_check_transactional_test_runner_release():
    """cargo check --release -p sui-transactional-test-runner must pass (pass_to_pass / origin: repo_tests)."""
    result = subprocess.run(
        ["cargo", "check", "--release", "-p", "sui-transactional-test-runner"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )

    assert result.returncode == 0, f"cargo check --release failed:\n{result.stderr.decode()}"


def test_claude_md_has_testing_guidance():
    """CLAUDE.md must include guidance on test-only code feature usage (origin: agent_config)."""
    claude_md = f"{REPO}/CLAUDE.md"
    with open(claude_md) as f:
        content = f.read()

    # Check for the new section on test-only code
    assert "### Test-Only Code" in content, "CLAUDE.md must have Test-Only Code section"
    assert '#[cfg(feature = "testing")]' in content, "Must document testing feature usage"
    assert "sui-types/testing" in content, "Must document feature propagation pattern"


def test_no_panic_on_gasless_in_release():
    """test_adapter.rs must not panic for gasless tokens in release mode (origin: static)."""
    test_adapter_rs = f"{REPO}/crates/sui-transactional-test-runner/src/test_adapter.rs"
    with open(test_adapter_rs) as f:
        content = f.read()

    # The old code had: panic!("gasless-allow-token is only supported in debug builds")
    assert "gasless-allow-token is only supported in debug builds" not in content, \
        "Must remove debug build panic for gasless tokens"

    # The new code should allow gasless tokens without the cfg(not(debug_assertions)) block
    assert "#[cfg(not(debug_assertions))]" not in content, \
        "Must remove debug_assertions conditional compilation"
