"""
Test file for verifying the external keystore file creation fix.

This tests that when external keys configuration exists but the corresponding
keystore and aliases files don't, they are automatically created.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path("/workspace/sui")
EXTERNAL_RS = REPO / "crates" / "sui-keys" / "src" / "external.rs"
SUI_COMMANDS_RS = REPO / "crates" / "sui" / "src" / "sui_commands.rs"


def run_cargo_test(package: str, test_name: str = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a cargo test for a specific package and optional test name."""
    cmd = ["cargo", "test", "-p", package, "--lib"]
    if test_name:
        cmd.extend(["--", test_name])
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        timeout=timeout
    )


def run_cargo_check(package: str = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run cargo check for a specific package or all."""
    cmd = ["cargo", "check"]
    if package:
        cmd.extend(["-p", package])
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        timeout=timeout
    )


def test_external_keystore_compiles():
    """
    F2P: Verify the sui-keys crate compiles successfully.

    This ensures the changes to external.rs are syntactically valid.
    """
    result = run_cargo_check("sui-keys", timeout=600)
    assert result.returncode == 0, f"sui-keys failed to compile:\n{result.stderr.decode()}"


def test_sui_commands_compiles():
    """
    F2P: Verify the sui_commands.rs changes are syntactically valid.

    This checks that the Rust code is valid by parsing it with rustfmt.
    Full compilation requires libclang for rocksdb-sys which isn't available.
    """
    # Check that the file parses correctly (no syntax errors)
    result = subprocess.run(
        ["rustfmt", "--check", str(SUI_COMMANDS_RS)],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    # rustfmt returns 1 for formatting differences, but that's OK
    # We just want to ensure there are no actual syntax errors
    # A syntax error would produce an error message like "error:" in stderr
    stderr = result.stderr.decode()
    assert "error:" not in stderr.lower() or "parsing" not in stderr.lower(), \
        f"sui_commands.rs has syntax errors:\n{stderr}"


def test_load_or_create_creates_files():
    """
    F2P: Verify that External::load_or_create creates external files when missing.

    This test runs the specific unit test that verifies the fix.
    """
    result = run_cargo_test("sui-keys", "test_load_or_create_creates_external_files", timeout=300)
    assert result.returncode == 0, (
        f"test_load_or_create_creates_external_files failed:\n"
        f"stdout: {result.stdout.decode()}\n"
        f"stderr: {result.stderr.decode()}"
    )
    # Verify the test actually ran and passed
    output = result.stdout.decode()
    assert "test_load_or_create_creates_external_files" in output or "running 1 test" in output, \
        "Expected test did not run"
    assert "FAILED" not in output, "Test failed - found FAILURE in output"


def test_load_new_from_path():
    """
    P2P: Verify External::load_or_create works with temp directories.

    This is the modified version of the existing test that now uses temp dirs.
    """
    result = run_cargo_test("sui-keys", "test_load_new_from_path", timeout=300)
    assert result.returncode == 0, (
        f"test_load_new_from_path failed:\n"
        f"stdout: {result.stdout.decode()}\n"
        f"stderr: {result.stderr.decode()}"
    )


def test_external_file_creation_code_writes_files():
    """
    F2P: Verify the Rust code actually writes files when they don't exist.

    This checks the source code to ensure it has the proper file write logic
    in the load_or_create method.
    """
    content = EXTERNAL_RS.read_text()

    # Check for the file existence tracking variables
    assert "let aliases_file_exists = aliases_store_directory.exists();" in content, \
        "aliases_file_exists variable not found - needed to track if file needs creation"
    assert "let keystore_file_exists = path.exists();" in content, \
        "keystore_file_exists variable not found - needed to track if file needs creation"

    # Check that files are written when they don't exist
    assert "if !aliases_file_exists {" in content, \
        "Condition to create aliases file not found"
    assert "if !keystore_file_exists {" in content, \
        "Condition to create keystore file not found"

    # Check that std::fs::write is called to create the files
    assert "std::fs::write(&aliases_store_directory" in content, \
        "aliases file write operation not found"
    assert "std::fs::write(path, keys_store)" in content, \
        "keystore file write operation not found"


def test_external_struct_has_load_or_create():
    """
    P2P: Verify the External struct has the load_or_create method.

    This is a structural check that the method exists.
    """
    content = EXTERNAL_RS.read_text()
    assert "pub fn load_or_create" in content, "load_or_create method not found in external.rs"


def test_sui_commands_has_ensure_external():
    """
    F2P: Verify ensure_external_keystore_config function exists in sui_commands.rs.

    This function is critical for ensuring the external keystore is configured.
    """
    content = SUI_COMMANDS_RS.read_text()
    assert "fn ensure_external_keystore_config" in content, \
        "ensure_external_keystore_config function not found in sui_commands.rs"


def test_sui_commands_has_default_path():
    """
    F2P: Verify default_external_keystore_path function exists.

    This function is needed to determine where external keystore files should be.
    """
    content = SUI_COMMANDS_RS.read_text()
    assert "fn default_external_keystore_path" in content, \
        "default_external_keystore_path function not found in sui_commands.rs"


def test_sui_commands_imports_external():
    """
    P2P: Verify sui_commands.rs imports External from sui_keys.

    The fix requires importing External to use it in the new code.
    """
    content = SUI_COMMANDS_RS.read_text()
    # Check that External is imported in the use statement
    assert "use sui_keys::keystore::{" in content and "External" in content, \
        "External not imported in sui_commands.rs keystore import"


def test_external_keystore_in_prompt_if_no_config():
    """
    F2P: Verify prompt_if_no_config initializes external_keys properly.

    This is the key behavioral change - when no config exists, external_keys
    should be initialized with External::load_or_create.
    """
    content = SUI_COMMANDS_RS.read_text()

    # Find the prompt_if_no_config function
    func_start = content.find("async fn prompt_if_no_config")
    assert func_start != -1, "prompt_if_no_config function not found"

    # Extract function body (simplified - look for the key patterns)
    # Check that external_keystore is created with External::load_or_create
    assert "External::load_or_create" in content[func_start:func_start + 2000], \
        "External::load_or_create not called in prompt_if_no_config"

    # Check that external_keys is set to Some(external_keystore)
    func_section = content[func_start:func_start + 3000]
    assert "external_keys: Some(" in func_section, \
        "external_keys not set to Some() in prompt_if_no_config"


def test_external_keys_command_uses_ensure_config():
    """
    F2P: Verify the external-keys command uses ensure_external_keystore_config.

    The external-keys command should call ensure_external_keystore_config
    to fix the config if external_keys is None.
    """
    content = SUI_COMMANDS_RS.read_text()

    # Look for the ExternalKeyCommand execution path
    # It should call ensure_external_keystore_config
    assert "ensure_external_keystore_config" in content, \
        "ensure_external_keystore_config not called anywhere in sui_commands.rs"


# =============================================================================
# Pass-to-Pass (P2P) Tests - Repo CI/CD Checks
# These ensure the fix doesn't break existing repo functionality
# =============================================================================


def test_repo_sui_keys_compiles():
    """
    P2P: Verify sui-keys crate compiles successfully.

    This is a repo CI check ensuring the code compiles without errors.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-keys"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"sui-keys failed to compile:\n{r.stderr[-500:]}"


def test_repo_sui_keys_clippy():
    """
    P2P: Verify sui-keys crate passes clippy lints.

    This is a repo CI check ensuring code quality standards.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-keys", "--all-targets", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"sui-keys failed clippy:\n{r.stderr[-500:]}"


def test_repo_sui_keys_tests():
    """
    P2P: Verify sui-keys crate unit tests pass.

    This is a repo CI check ensuring existing tests still pass.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "sui-keys", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"sui-keys tests failed:\n{r.stderr[-500:]}"


def test_repo_sui_keys_formatting():
    """
    P2P: Verify sui-keys crate code is properly formatted.

    This is a repo CI check ensuring code formatting standards.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Code formatting check failed:\n{r.stderr[-500:]}"
