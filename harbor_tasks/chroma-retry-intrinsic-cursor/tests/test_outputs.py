"""
Tests for chroma-core/chroma PR #6703: Add retry logic to update_intrinsic_cursor.

These tests verify that:
1. The backon dependency is added to Cargo.toml
2. The retry logic is correctly implemented with proper parameters
3. The code compiles successfully
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/workspace/chroma")
LOG_SERVICE_DIR = REPO_ROOT / "rust" / "log-service"


def test_backon_dependency_added():
    """Fail-to-pass: Verify backon dependency is added to log-service/Cargo.toml"""
    cargo_toml = LOG_SERVICE_DIR / "Cargo.toml"
    content = cargo_toml.read_text()

    assert 'backon = { workspace = true }' in content, \
        "backon dependency not found in Cargo.toml"


def test_backon_import_present():
    """Fail-to-pass: Verify backon is imported in lib.rs"""
    lib_rs = LOG_SERVICE_DIR / "src" / "lib.rs"
    content = lib_rs.read_text()

    assert 'use backon::{ExponentialBuilder, Retryable};' in content, \
        "backon import not found in lib.rs"


def test_retry_logic_structure():
    """Fail-to-pass: Verify retry closure pattern is used"""
    lib_rs = LOG_SERVICE_DIR / "src" / "lib.rs"
    content = lib_rs.read_text()

    # Check for the retry closure pattern
    assert 'let witness = (|| {' in content, \
        "Retry closure pattern not found"
    assert '}).retry(' in content, \
        ").retry() call not found"


def test_exponential_builder_params():
    """Fail-to-pass: Verify exponential backoff parameters are correct"""
    lib_rs = LOG_SERVICE_DIR / "src" / "lib.rs"
    content = lib_rs.read_text()

    # Check for specific retry parameters
    assert 'with_min_delay(Duration::from_millis(20))' in content, \
        "Min delay (20ms) not found"
    assert 'with_max_delay(Duration::from_millis(200))' in content, \
        "Max delay (200ms) not found"
    assert 'with_max_times(3)' in content, \
        "Max times (3) not found"


def test_precondition_error_filter():
    """Fail-to-pass: Verify retry only triggers on Precondition errors"""
    lib_rs = LOG_SERVICE_DIR / "src" / "lib.rs"
    content = lib_rs.read_text()

    # Check for the when clause that filters on Precondition errors
    assert '.when(|err: &wal3::Error|' in content, \
        "Retry when clause not found"
    assert 'chroma_storage::StorageError::Precondition' in content, \
        "StorageError::Precondition check not found"
    assert 'matches!(' in content, \
        "matches! macro for error filtering not found"


def test_cargo_check_passes():
    """Pass-to-pass: Verify code compiles after changes"""
    result = subprocess.run(
        ["cargo", "check", "-p", "chroma-log-service"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"cargo check failed:\n{result.stderr}"


def test_cargo_lock_updated():
    """Pass-to-pass: Verify Cargo.lock includes backon for log-service"""
    cargo_lock = REPO_ROOT / "Cargo.lock"
    content = cargo_lock.read_text()

    # Find the log-service package section and verify backon is listed
    # This is a structural check that backon is in the dependency tree
    lines = content.split('\n')
    in_log_service = False
    found_backon = False

    for line in lines:
        if 'name = "chroma-log-service"' in line:
            in_log_service = True
        elif in_log_service and line.strip().startswith('name = ') and 'chroma-log-service' not in line:
            in_log_service = False
        elif in_log_service and 'backon' in line:
            found_backon = True
            break

    assert found_backon, \
        "backon dependency not found in Cargo.lock for chroma-log-service"


def test_no_blocking_sync_in_retry():
    """Fail-to-pass: Verify retry uses async pattern correctly"""
    lib_rs = LOG_SERVICE_DIR / "src" / "lib.rs"
    content = lib_rs.read_text()

    # Ensure we're using async move in the closure
    assert 'async move {' in content, \
        "async move block not found in retry closure"

    # Ensure we're using .await after the retry chain
    retry_section = content[content.find('.retry('):content.find('.await', content.find('.retry(')) + 10]
    assert '.await' in retry_section, \
        ".await not found after retry block"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
