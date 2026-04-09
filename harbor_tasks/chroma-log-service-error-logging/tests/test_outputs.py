"""
Tests for chroma-core/chroma PR #6718: Add error logging for Status::unknown responses.

This verifies that tracing::error! calls are added to three error paths in PushLogs:
1. get_log_from_handle failure
2. proto encode failure
3. append_many failure
"""

import subprocess
import sys
import re

REPO = "/workspace/chroma"
TARGET_FILE = f"{REPO}/rust/log-service/src/lib.rs"


def test_compilation():
    """Verify the Rust code compiles successfully."""
    # Install protoc first as it's needed for the build
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        cwd=REPO,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "protobuf-compiler"],
        capture_output=True,
        cwd=REPO,
    )
    result = subprocess.run(
        ["cargo", "check", "--package", "chroma-log-service"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr[-1000:]}"


def test_get_log_from_handle_error_logging():
    """Verify tracing::error! is called for get_log_from_handle failure."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the pattern where get_log_from_handle error is logged
    # The error should be in the Err(err) arm of a match on get_log_from_handle result
    pattern = r'Err\(err\)\s*=>\s*\{[^}]*tracing::error!\(err\s*=\s*%err,\s*"get_log_from_handle failure"\)'

    assert re.search(pattern, content, re.DOTALL), \
        "tracing::error! call for 'get_log_from_handle failure' not found in error handler"


def test_proto_encode_error_logging():
    """Verify tracing::error! is called for proto encode failure."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the pattern where proto encode error is logged
    # The error should be in the map_err closure for record.encode()
    pattern = r'record\.encode\(&mut buf\)\.map_err\(\|err\|\s*\{[^}]*tracing::error!\(err\s*=\s*%err,\s*"proto encode failure"\)'

    assert re.search(pattern, content, re.DOTALL), \
        "tracing::error! call for 'proto encode failure' not found in encode error handler"


def test_append_many_error_logging():
    """Verify tracing::error! is called for append_many failure."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the pattern where append_many error is logged
    # The error should be in the Err(err) arm of the append_many result match
    pattern = r'append_many.*\n.*Err\(err\)\s*=>\s*\{[^}]*tracing::error!\(err\s*=\s*%err,\s*"append_many failure"\)'

    assert re.search(pattern, content, re.DOTALL), \
        "tracing::error! call for 'append_many failure' not found in error handler"


def test_error_logs_use_percent_display():
    """Verify error logging uses %err (Display trait) for proper error formatting."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that all three error logs use %err format
    error_patterns = [
        'tracing::error!(err = %err, "get_log_from_handle failure")',
        'tracing::error!(err = %err, "proto encode failure")',
        'tracing::error!(err = %err, "append_many failure")',
    ]

    for pattern in error_patterns:
        assert pattern in content, f"Expected error log pattern not found: {pattern}"


def test_error_logs_before_status_return():
    """Verify error logging happens before returning Status::unknown or Status::new."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Each error log should be followed by a return of Status in the same block
    # Check get_log_from_handle pattern
    get_log_pattern = r'tracing::error!\(err\s*=\s*%err,\s*"get_log_from_handle failure"\);\s*return\s+Err\(Status::unknown'
    assert re.search(get_log_pattern, content), \
        "get_log_from_handle error log should be followed by return Err(Status::unknown(...))"

    # Check proto encode pattern
    encode_pattern = r'tracing::error!\(err\s*=\s*%err,\s*"proto encode failure"\);\s*Status::unknown'
    assert re.search(encode_pattern, content), \
        "proto encode error log should be followed by Status::unknown(...)"

    # Check append_many pattern
    append_pattern = r'tracing::error!\(err\s*=\s*%err,\s*"append_many failure"\);\s*return\s+Err\(Status::new'
    assert re.search(append_pattern, content), \
        "append_many error log should be followed by return Err(Status::new(...))"


# Pass-to-pass tests: repo's CI/CD checks that should pass on both base and fixed

def test_repo_cargo_check():
    """Repo's cargo check passes on log-service (pass_to_pass)."""
    # Install protoc first as it's needed for the build
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        cwd=REPO,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "protobuf-compiler"],
        capture_output=True,
        cwd=REPO,
    )
    r = subprocess.run(
        ["cargo", "check", "--package", "chroma-log-service"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_clippy():
    """Repo's cargo clippy passes on log-service (pass_to_pass)."""
    # Install protoc first as it's needed for the build
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        cwd=REPO,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "protobuf-compiler"],
        capture_output=True,
        cwd=REPO,
    )
    r = subprocess.run(
        ["cargo", "clippy", "--package", "chroma-log-service", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo clippy failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    import os
    # Check if we're in stub mode (for self-audit)
    if os.environ.get("STUB_TEST"):
        print("Running in stub mode - all tests should fail")
        sys.exit(1)

    pytest.main([__file__, "-v"])
