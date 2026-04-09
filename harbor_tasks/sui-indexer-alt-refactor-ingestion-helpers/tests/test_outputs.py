"""Tests for sui-indexer-alt-framework refactoring task.

This task verifies that the ingestion client has been refactored to use
helper functions for backoff and retry logic with slow-operation monitoring.
"""

import subprocess
import sys

REPO = "/workspace/sui"
INGESTION_CLIENT_PATH = "crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs"
METRICS_PATH = "crates/sui-indexer-alt-framework/src/metrics.rs"


def test_cargo_check():
    """Verify the code compiles successfully."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_transient_backoff_function_exists():
    """Verify the transient_backoff helper function exists."""
    result = subprocess.run(
        ["grep", "-n", "fn transient_backoff", INGESTION_CLIENT_PATH],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "transient_backoff function not found"
    # Verify it returns ExponentialBackoff
    assert "ExponentialBackoff" in result.stdout, "Function should return ExponentialBackoff"


def test_retry_transient_with_slow_monitor_exists():
    """Verify the retry_transient_with_slow_monitor helper function exists."""
    result = subprocess.run(
        ["grep", "-n", "async fn retry_transient_with_slow_monitor", INGESTION_CLIENT_PATH],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "retry_transient_with_slow_monitor function not found"


def test_retry_function_signature():
    """Verify the retry function has the correct signature with proper parameters."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # Check for key signature elements
    assert "async fn retry_transient_with_slow_monitor<F, Fut, T>" in content, \
        "Function should be generic over F, Fut, T"
    assert "operation: &str" in content, "Function should take operation name parameter"
    assert "make_future: F" in content, "Function should take make_future closure"
    assert "latency: &Histogram" in content, "Function should take latency histogram parameter"


def test_uses_with_slow_future_monitor():
    """Verify the retry function uses with_slow_future_monitor."""
    result = subprocess.run(
        ["grep", "-A", "20", "async fn retry_transient_with_slow_monitor", INGESTION_CLIENT_PATH],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert "with_slow_future_monitor" in result.stdout, \
        "retry_transient_with_slow_monitor should call with_slow_future_monitor"


def test_checkpoint_uses_new_helper():
    """Verify checkpoint method uses the new retry_transient_with_slow_monitor helper."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # Check that checkpoint method calls the new helper
    assert "retry_transient_with_slow_monitor(" in content, \
        "checkpoint method should call retry_transient_with_slow_monitor"


def test_chain_id_uses_new_helper():
    """Verify chain_id fetching uses the new retry_transient_with_slow_monitor helper."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # Count occurrences of the helper - should be at least 2 (checkpoint + chain_id)
    count = content.count("retry_transient_with_slow_monitor(")
    assert count >= 2, f"Expected at least 2 calls to retry_transient_with_slow_monitor, found {count}"


def test_ingested_chain_id_latency_metric_exists():
    """Verify the new ingested_chain_id_latency metric was added."""
    result = subprocess.run(
        ["grep", "ingested_chain_id_latency", METRICS_PATH],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "ingested_chain_id_latency metric not found in metrics.rs"


def test_metric_registered():
    """Verify the metric is properly registered in the constructor."""
    with open(f"{REPO}/{METRICS_PATH}", "r") as f:
        content = f.read()

    # Check that the metric is registered
    assert "ingested_chain_id_latency:" in content, \
        "Metric should be declared in IngestionMetrics struct"
    assert "ingested_chain_id_latency: register_histogram_with_registry!" in content, \
        "Metric should be registered with register_histogram_with_registry!"


def test_unit_tests_compile():
    """Verify unit tests compile successfully."""
    result = subprocess.run(
        ["cargo", "test", "--no-run", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Tests failed to compile:\n{result.stderr}"


# ===== Pass-to-Pass CI/CD Tests =====
# These verify the repo's own CI checks pass on both base and after fix


def test_p2p_cargo_check():
    """Repo's cargo check passes (pass_to_pass).

    Verifies that the sui-indexer-alt-framework crate compiles without errors.
    This is the repo's basic compilation check.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_p2p_cargo_clippy():
    """Repo's clippy linting passes (pass_to_pass).

    Verifies that the sui-indexer-alt-framework crate passes clippy lints.
    This is the repo's linting check equivalent to 'cargo xclippy'.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-indexer-alt-framework", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-1000:]}"


def test_p2p_cargo_test_compile():
    """Repo's tests compile successfully (pass_to_pass).

    Verifies that the test code for sui-indexer-alt-framework compiles.
    Uses --no-run to only check compilation without running tests.
    """
    r = subprocess.run(
        ["cargo", "test", "--no-run", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo test --no-run failed:\n{r.stderr[-1000:]}"


def test_p2p_cargo_fmt_check():
    """Repo's code formatting passes (pass_to_pass).

    Verifies that the sui-indexer-alt-framework crate code is properly formatted.
    Uses --check to verify without modifying files.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


def test_imports_updated():
    """Verify necessary imports were added."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # Check for new imports
    assert "use std::future::Future;" in content, "Should import Future trait"
    assert "use prometheus::Histogram;" in content, "Should import Histogram type"


def test_error_alias_used():
    """Verify the IE (IngestionError) alias is used consistently."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # Check that the IE alias is defined and used
    assert "use crate::ingestion::Error as IE;" in content, \
        "Should use Error as IE alias"


def test_old_get_or_init_chain_id_removed():
    """Verify the old get_or_init_chain_id method was removed."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # The old method should no longer exist
    assert "async fn get_or_init_chain_id" not in content, \
        "Old get_or_init_chain_id method should have been removed"


def test_parallel_fetching():
    """Verify that checkpoint and chain_id are fetched concurrently using try_join."""
    with open(f"{REPO}/{INGESTION_CLIENT_PATH}", "r") as f:
        content = f.read()

    # Check for tokio::try_join! usage
    assert "tokio::try_join!" in content, \
        "Should use tokio::try_join! for concurrent fetching"
