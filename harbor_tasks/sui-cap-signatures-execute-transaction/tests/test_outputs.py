#!/usr/bin/env python3
"""
Tests for PR: Cap the number of signatures in execute_transaction

Validates that the gRPC execute_transaction endpoint rejects requests
with more than 2 signatures (max allowed: 1 for sender + 1 for sponsor).
"""

import subprocess
import re
import os

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs"


def test_signature_limit_constant_exists():
    """Fail-to-pass: MAX_NUMBER_OF_SIGNATURES constant must be defined."""
    file_path = os.path.join(REPO, TARGET_FILE)
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for the constant definition
    assert "MAX_NUMBER_OF_SIGNATURES" in content, \
        "MAX_NUMBER_OF_SIGNATURES constant not found"

    # Verify it has the right value (2)
    pattern = r"const\s+MAX_NUMBER_OF_SIGNATURES:\s*usize\s*=\s*2"
    assert re.search(pattern, content), \
        "MAX_NUMBER_OF_SIGNATURES constant should be set to 2"


def test_signature_validation_code_exists():
    """Fail-to-pass: Signature count validation must be implemented."""
    file_path = os.path.join(REPO, TARGET_FILE)
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for the validation logic
    assert "request.signatures.len()" in content, \
        "Signature length check not found"

    # Check for the error message about exceeding maximum
    assert "exceeds the maximum allowed" in content, \
        "Error message about exceeding maximum not found"


def test_validation_occurs_before_signature_parsing():
    """Fail-to-pass: Validation must happen before signature parsing."""
    file_path = os.path.join(REPO, TARGET_FILE)
    with open(file_path, 'r') as f:
        content = f.read()

    # Find the execute_transaction function and check structure
    # The validation should come before the signature parsing loop
    func_start = content.find("pub async fn execute_transaction")
    assert func_start != -1, "execute_transaction function not found"

    func_content = content[func_start:]

    # Find key markers
    validation_marker = "request.signatures.len() > MAX_NUMBER_OF_SIGNATURES"
    parsing_marker = "let signatures = request"

    validation_pos = func_content.find(validation_marker)
    parsing_pos = func_content.find(parsing_marker)

    assert validation_pos != -1, "Validation check not found in function"
    assert parsing_pos != -1, "Signature parsing not found in function"
    assert validation_pos < parsing_pos, \
        "Validation must occur before signature parsing"


def test_error_is_invalid_argument():
    """Fail-to-pass: Error must use FieldInvalid reason for InvalidArgument."""
    file_path = os.path.join(REPO, TARGET_FILE)
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for FieldViolation with signatures field
    assert 'FieldViolation::new("signatures")' in content, \
        "FieldViolation::new('signatures') not found"

    # Check for ErrorReason::FieldInvalid
    assert "ErrorReason::FieldInvalid" in content, \
        "ErrorReason::FieldInvalid not found in validation"


def test_cargo_check_passes():
    """Pass-to-pass: Code must compile without errors."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-rpc-api"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    if result.returncode != 0:
        # Only fail on errors, not warnings
        error_lines = [line for line in result.stderr.split('\n')
                      if 'error[' in line or line.strip().startswith('error:')]
        assert not error_lines, f"Compilation errors found:\n{result.stderr[-1000:]}"


def test_cargo_clippy_passes():
    """Pass-to-pass: Clippy lints must pass for sui-rpc-api (repo CI/CD)."""
    result = subprocess.run(
        [
            "cargo", "clippy", "-p", "sui-rpc-api",
            "--all-targets", "--all-features", "--",
            "-Wclippy::all",
            "-Wclippy::disallowed_methods",
            "-Aclippy::unnecessary_get_then_check",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    if result.returncode != 0:
        # Only fail on errors, not warnings
        error_lines = [line for line in result.stderr.split('\n')
                      if 'error[' in line or line.strip().startswith('error:')]
        assert not error_lines, f"Clippy errors found:\n{result.stderr[-1000:]}"


def test_cargo_fmt_check_passes():
    """Pass-to-pass: Code must be properly formatted (repo CI/CD)."""
    result = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Format check returns non-zero if files need formatting
    assert result.returncode == 0, f"Code formatting issues found:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_cargo_test_sui_rpc_api_passes():
    """Pass-to-pass: sui-rpc-api tests must type-check (repo CI/CD).

    Note: In resource-constrained environments, we use cargo check --tests
    which verifies tests compile without the disk space overhead of full
    test compilation with linking.
    """
    result = subprocess.run(
        ["cargo", "check", "--tests", "-p", "sui-rpc-api"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    assert result.returncode == 0, f"Tests failed to compile:\n{result.stderr[-1000:]}"


def test_cargo_xlint_passes():
    """Pass-to-pass: License check passes (repo CI/CD).

    cargo xlint verifies that all source files have proper license headers
    (Copyright (c) Mysten Labs, Inc. and SPDX-License-Identifier: Apache-2.0).
    This is run in CI to ensure license compliance.
    """
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, f"License check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_code_has_proper_documentation():
    """Fail-to-pass: Constant must have explanatory comment."""
    file_path = os.path.join(REPO, TARGET_FILE)
    with open(file_path, 'r') as f:
        content = f.read()

    # Find the MAX_NUMBER_OF_SIGNATURES constant and check preceding comment
    const_pos = content.find("const MAX_NUMBER_OF_SIGNATURES")
    assert const_pos != -1, "Constant not found"

    # Look at the lines before the constant for a comment
    before_const = content[:const_pos]
    lines_before = before_const.split('\n')[-5:]  # Last 5 lines before constant

    comment_found = any(
        line.strip().startswith('//') and ('signature' in line.lower() or 'sender' in line.lower() or 'sponsor' in line.lower())
        for line in lines_before
    )

    assert comment_found, \
        "Constant should have a comment explaining the limit (sender + sponsor)"
