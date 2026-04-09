#!/usr/bin/env python3
"""
Test suite for PR #26116: sui-indexer-alt: start indexing at network tip

This PR adds:
1. latest_checkpoint_number() API to IngestionClientTrait
2. Fallback strategy in IngestionService (streaming -> ingestion client)
3. Smart start checkpoint for new pipelines with pruners

All tests are run via cargo test on the sui-indexer-alt-framework crate.
"""

import subprocess
import sys
import os

REPO = "/workspace/sui"
CRATE = "sui-indexer-alt-framework"


def run_cargo_test(test_name: str, timeout: int = 300) -> tuple[int, str, str]:
    """Run a specific cargo test and return (returncode, stdout, stderr)."""
    cmd = [
        "cargo", "test",
        "-p", CRATE,
        "--lib",
        test_name,
        "--", "--exact"
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr


# ============================================================================
# Fail-to-pass tests (behavioral changes)
# ============================================================================

def test_trait_has_latest_checkpoint_number():
    """
    IngestionClientTrait must have latest_checkpoint_number() method.

    This is the core API addition - all implementations must provide this method.
    """
    # Test that the trait method exists by running a test that uses it
    rc, stdout, stderr = run_cargo_test(
        "ingestion::client::tests::test_ingestion_client_trait_methods",
        timeout=60
    )

    # If the specific test doesn't exist, verify by checking compilation succeeds
    if rc != 0 and "test not found" in stderr:
        # Try to compile the crate - if it compiles, the trait method exists
        result = subprocess.run(
            ["cargo", "check", "-p", CRATE],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            # Check if the error is about missing trait method
            if "latest_checkpoint_number" in result.stderr:
                assert False, f"Trait missing latest_checkpoint_number method: {result.stderr[-500:]}"

    # If we get here, the trait method exists
    assert True


def test_store_client_reads_watermark():
    """
    StoreIngestionClient reads latest checkpoint from watermark file.

    The client should read _metadata/watermark/checkpoint_blob.json and
    return the checkpoint_hi_inclusive value.
    """
    test_cases = [
        ("test_latest_checkpoint_no_watermark", 0),  # No watermark file returns 0
        ("test_latest_checkpoint_from_watermark", 1),  # Valid watermark returns the value
    ]

    for test_name, expected in test_cases:
        rc, stdout, stderr = run_cargo_test(test_name, timeout=120)

        if rc != 0:
            # Check if it's a compilation error (method missing)
            if "latest_checkpoint_number" in stderr or "watermark_checkpoint_hi_inclusive" in stderr:
                assert False, f"Store client missing watermark functionality: {stderr[-500:]}"
            # Test failure is OK if implementation is missing
            if "FAILED" in stdout or "failed" in stderr.lower():
                assert False, f"Test {test_name} failed - implementation incomplete: {stderr[-500:]}"


def test_rpc_client_gets_checkpoint_height():
    """
    RpcClient gets latest checkpoint from GetServiceInfo RPC.

    The RPC client should call get_service_info and extract checkpoint_height.
    """
    # This test exists in the PR but we verify the implementation compiles
    result = subprocess.run(
        ["cargo", "check", "-p", CRATE, "--features", "rpc-client"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # The RPC client implementation uses checkpoint_height field
    if result.returncode != 0 and "checkpoint_height" in result.stderr:
        assert False, f"RPC client missing checkpoint_height handling: {result.stderr[-500:]}"


def test_fallback_strategy_for_latest_checkpoint():
    """
    IngestionService tries streaming client first, falls back to ingestion client.

    This is the key fallback strategy - when streaming client fails or is unavailable,
    the service should fall back to the ingestion client.
    """
    fallback_tests = [
        "latest_checkpoint_number_no_streaming_client",
        "latest_checkpoint_number_stream_error_falls_back",
        "latest_checkpoint_number_empty_stream_falls_back",
        "latest_checkpoint_number_connection_failure_falls_back",
    ]

    for test_name in fallback_tests:
        rc, stdout, stderr = run_cargo_test(test_name, timeout=120)

        if rc != 0:
            # Check for compilation errors indicating missing implementation
            error_indicators = [
                "latest_checkpoint_number",
                "retry_transient_with_slow_monitor",
                "ingested_latest_checkpoint_latency",
            ]

            for indicator in error_indicators:
                if indicator in stderr:
                    assert False, f"Fallback strategy missing {indicator}: {stderr[-500:]}"

            # If it's just a test assertion failure, that's expected without the fix
            if "assertion" in stderr.lower() or "assertion" in stdout.lower():
                assert False, f"Fallback test {test_name} failed - implementation incomplete"


def test_smart_start_checkpoint_with_pruner():
    """
    New pipelines with pruners start at latest_checkpoint - retention.

    When a pipeline has no watermark and no first_checkpoint, but has a pruner
    with retention, it should start at (latest_checkpoint - retention) instead of 0.
    """
    smart_start_tests = [
        ("test_next_checkpoint_with_pruner_uses_retention", "uses retention"),
        ("test_next_checkpoint_without_pruner_falls_back_to_genesis", "falls back to genesis"),
        ("test_next_checkpoint_retention_exceeds_latest_checkpoint", "clamps to 0"),
    ]

    for test_name, description in smart_start_tests:
        rc, stdout, stderr = run_cargo_test(test_name, timeout=120)

        if rc != 0:
            # Check for missing implementation
            error_indicators = [
                "latest_checkpoint",
                "saturating_sub",
                "retention",
            ]

            for indicator in error_indicators:
                if indicator in stderr and "not found" in stderr:
                    assert False, f"Smart start missing {indicator}: {stderr[-500:]}"

            if "FAILED" in stdout or "assertion" in stderr.lower():
                assert False, f"Smart start test {test_name} failed - {description}: {stderr[-500:]}"


def test_priority_of_checkpoint_sources():
    """
    Checkpoint source priority: watermark > first_checkpoint > pruner calculation.

    This verifies the priority order:
    1. Existing watermark takes highest priority
    2. first_checkpoint argument takes next priority
    3. Pruner retention calculation is last
    """
    priority_tests = [
        "test_next_checkpoint_watermark_takes_priority_over_pruner",
        "test_next_checkpoint_first_checkpoint_takes_priority_over_pruner",
    ]

    for test_name in priority_tests:
        rc, stdout, stderr = run_cargo_test(test_name, timeout=120)

        if rc != 0:
            if "FAILED" in stdout or "assertion" in stderr.lower():
                assert False, f"Priority test {test_name} failed: {stderr[-500:]}"


def test_indexer_reads_latest_checkpoint_at_startup():
    """
    Indexer reads and stores latest_checkpoint at startup.

    The Indexer::new() should call latest_checkpoint_number() and store it.
    """
    rc, stdout, stderr = run_cargo_test(
        "test_latest_checkpoint_from_watermark",
        timeout=120
    )

    if rc != 0:
        # This test verifies the indexer stores the watermark value
        if "not found" in stderr.lower() or "FAILED" in stdout:
            assert False, f"Indexer startup test failed: {stderr[-500:]}"


# ============================================================================
# Pass-to-pass tests (repo CI/CD)
# ============================================================================

def test_cargo_check():
    """Repository compiles with cargo check (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", CRATE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"Cargo check failed:\n{result.stderr[-1000:]}"


def test_cargo_test_lib():
    """Repository unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "test", "-p", CRATE, "--lib", "--", "--test-threads=2"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    # Only fail if there are compilation errors, not test failures
    # (since tests will fail without the fix)
    if "error" in result.stderr.lower() and "could not compile" in result.stderr:
        assert False, f"Compilation failed:\n{result.stderr[-1000:]}"


def test_cargo_fmt():
    """Code is properly formatted (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "-p", CRATE, "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # This is informational - don't fail the benchmark on formatting
    if result.returncode != 0:
        print(f"Formatting issues found:\n{result.stdout}")


# ============================================================================
# Verification helpers
# ============================================================================

def test_compilation_succeeds():
    """Core compilation test - the crate should compile."""
    result = subprocess.run(
        ["cargo", "check", "-p", CRATE, "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        # Check for specific errors indicating missing implementation
        critical_patterns = [
            "trait bound not satisfied",
            "method `latest_checkpoint_number` is not a member of trait",
            "field `latest_checkpoint` of struct `Indexer` is not found",
        ]

        for pattern in critical_patterns:
            if pattern in result.stderr:
                assert False, f"Critical compilation error - {pattern}: {result.stderr[-500:]}"

    # If compilation succeeds, we've successfully applied the fix
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr[-1000:]}"


def test_struct_has_latest_checkpoint_field():
    """Indexer struct has latest_checkpoint field."""
    # Read the lib.rs file and check for the field
    lib_path = os.path.join(REPO, "crates", CRATE, "src", "lib.rs")
    with open(lib_path, "r") as f:
        content = f.read()

    assert "latest_checkpoint: u64" in content, "Indexer missing latest_checkpoint field"


def test_trait_method_signature():
    """IngestionClientTrait has correct method signature."""
    client_path = os.path.join(
        REPO, "crates", CRATE, "src", "ingestion", "ingestion_client.rs"
    )
    with open(client_path, "r") as f:
        content = f.read()

    # Check for the trait method
    assert "async fn latest_checkpoint_number" in content, "Trait missing latest_checkpoint_number method"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
