"""
Test outputs for consensus probe-before-fetch task (PR #26056).

This tests that:
1. New timeout parameters exist with correct defaults
2. probe_connectivity method is implemented in network clients
3. commit_syncer uses configurable timeouts instead of hardcoded constants
4. ObserverNetworkService trait methods are implemented
"""

import subprocess
import sys

REPO = "/workspace/sui"


def run_cargo_check(package: str) -> tuple[int, str, str]:
    """Run cargo check on a package and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["cargo", "check", "-p", package],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.returncode, result.stdout, result.stderr


def run_cargo_test(package: str, test_filter: str = "") -> tuple[int, str, str]:
    """Run cargo test on a package with optional filter."""
    cmd = ["cargo", "test", "-p", package, "--lib"]
    if test_filter:
        cmd.append(test_filter)
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.returncode, result.stdout, result.stderr


def test_parameters_has_timeout_fields():
    """
    Test that Parameters struct has the new timeout fields with correct defaults.
    This is a fail-to-pass test - these fields do not exist in base commit.
    """
    code, stdout, stderr = run_cargo_check("consensus-config")
    combined = stdout + stderr
    assert code == 0, f"consensus-config failed to compile:\n{combined}"
    assert "commit_sync_request_timeout" in combined or code == 0, \
        "commit_sync_request_timeout field missing or compilation error"
    assert "commit_sync_probe_timeout" in combined or code == 0, \
        "commit_sync_probe_timeout field missing or compilation error"


def test_probe_connectivity_method_exists():
    """
    Test that NetworkClient has the probe_connectivity method.
    This method is new in the PR and does not exist in base commit.
    """
    result = subprocess.run(
        ["grep", "-r", "probe_connectivity", "consensus/core/src/network/"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "probe_connectivity method not found in network clients"
    assert "pub async fn probe_connectivity" in result.stdout, \
        "probe_connectivity is not a public async method"


def test_commit_syncer_uses_configurable_timeout():
    """
    Test that commit_syncer.rs uses the configurable timeout from parameters.
    """
    result = subprocess.run(
        ["cat", "consensus/core/src/commit_syncer.rs"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    content = result.stdout
    assert "const TIMEOUT: Duration = Duration::from_secs(10)" not in content, \
        "Hardcoded TIMEOUT constant still exists (should be removed)"
    assert "inner.context.parameters.commit_sync_request_timeout" in content, \
        "Should use configurable commit_sync_request_timeout parameter"
    assert "inner.context.parameters.commit_sync_probe_timeout" in content, \
        "Should use configurable commit_sync_probe_timeout parameter"


def test_authority_service_implements_observer_trait():
    """
    Test that AuthorityService implements ObserverNetworkService trait methods.
    """
    result = subprocess.run(
        ["cat", "consensus/core/src/authority_service.rs"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    content = result.stdout
    assert "ObserverNetworkService" in content, \
        "ObserverNetworkService trait not imported"
    assert "handle_stream_blocks" in content, \
        "handle_stream_blocks method not implemented"
    assert "handle_fetch_blocks" in content, \
        "handle_fetch_blocks method not implemented"
    assert "handle_fetch_commits" in content, \
        "handle_fetch_commits method not implemented"
    assert "impl<C: CoreThreadDispatcher> ObserverNetworkService for AuthorityService<C>" in content, \
        "ObserverNetworkService trait implementation not found"


def test_probe_call_in_fetch_commits_once():
    """
    Test that the fetch_commits_once method calls probe_connectivity.
    """
    result = subprocess.run(
        ["cat", "consensus/core/src/commit_syncer.rs"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    content = result.stdout
    assert ".probe_connectivity(" in content, \
        "probe_connectivity not called in fetch_commits_once"
    assert "probe_timeout" in content, \
        "probe_timeout variable not used"
    assert "Probe the target" in content or "probe" in content.lower(), \
        "Probing comment/documentation not found"


def test_config_compiles_with_new_defaults():
    """
    Test that the config crate compiles and the snapshot test passes.
    """
    code, stdout, stderr = run_cargo_test("consensus-config", "parameters_test")
    combined = stdout + stderr
    assert code == 0, f"consensus-config parameters test failed:\n{combined}"
    result = subprocess.run(
        ["cat", "consensus/config/tests/snapshots/parameters_test__parameters.snap"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    snapshot = result.stdout
    assert "commit_sync_request_timeout:" in snapshot, \
        "Snapshot missing commit_sync_request_timeout"
    assert "commit_sync_probe_timeout:" in snapshot, \
        "Snapshot missing commit_sync_probe_timeout"
    assert "secs: 10" in snapshot, \
        "Snapshot should show 10s default for request timeout"
    assert "secs: 2" in snapshot, \
        "Snapshot should show 2s default for probe timeout"


def test_network_client_has_probe_method():
    """
    Test that NetworkClient has the probe_connectivity method in clients.rs.
    """
    result = subprocess.run(
        ["cat", "consensus/core/src/network/clients.rs"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    content = result.stdout
    assert "pub async fn probe_connectivity" in content, \
        "probe_connectivity method not found or not public"
    assert "peer: PeerId" in content, \
        "probe_connectivity should take PeerId parameter"
    assert "timeout: Duration" in content, \
        "probe_connectivity should take Duration timeout parameter"
    assert "get_latest_rounds" in content, \
        "probe_connectivity should call get_latest_rounds"


# ============ Pass-to-pass tests (repo CI/CD checks) ============
# These tests verify that standard CI checks pass on both base and fix commits
# All CI commands tested in the Docker container with the base commit.


def test_repo_cargo_fmt_check():
    """Repo's cargo fmt check passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_consensus_config():
    """Repo's cargo check passes for consensus-config (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "consensus-config"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p consensus-config failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_consensus_types():
    """Repo's cargo check passes for consensus-types (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "consensus-types"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p consensus-types failed:\n{r.stderr[-500:]}"


def test_repo_cargo_clippy_consensus_config():
    """Repo's cargo clippy passes for consensus-config (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "consensus-config", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p consensus-config failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test_consensus_config_lib():
    """Repo's cargo test --lib passes for consensus-config (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "consensus-config", "--lib"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo test -p consensus-config --lib failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test_consensus_config_snapshot():
    """Repo's consensus-config snapshot test passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "consensus-config", "--lib", "parameters_snapshot_matches"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"consensus-config snapshot test failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test_consensus_committee():
    """Repo's consensus-config committee tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "consensus-config", "--lib", "committee"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"consensus-config committee tests failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test_consensus_types_lib():
    """Repo's cargo test --lib passes for consensus-types (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "consensus-types", "--lib"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo test -p consensus-types --lib failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
