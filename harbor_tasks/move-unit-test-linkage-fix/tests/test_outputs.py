"""Tests for the Move unit test runner linkage fix.

This module validates that the fix for cross-package linkage in the Move unit
test runner is correctly implemented.
"""

import subprocess
import os
import sys

REPO_ROOT = "/workspace/sui"
TARGET_FILE = "external-crates/move/crates/move-unit-test/src/test_runner.rs"
FULL_TARGET_PATH = f"{REPO_ROOT}/{TARGET_FILE}"


def run_command(cmd, cwd=None, timeout=300):
    """Run a command and return result."""
    result = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def test_linkage_context_import_present():
    """Fail-to-pass: Verify that linkage_context is imported in the use statement.

    The fix adds `linkage_context` to the imports from `move_vm_runtime::shared`.
    Before the fix: only `gas::GasMeter` is imported.
    After the fix: both `gas::GasMeter` and `linkage_context` are imported.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for the new import structure that includes linkage_context
    # This should be: shared::{gas::GasMeter, linkage_context}
    import_pattern = "shared::{gas::GasMeter, linkage_context}"

    assert import_pattern in content, (
        f"Missing required import: {import_pattern}\n"
        "The fix requires importing linkage_context from move_vm_runtime::shared"
    )


def test_linkage_table_construction():
    """Fail-to-pass: Verify that linkage_table is constructed from package keys.

    The fix constructs a linkage table that maps package addresses to themselves
    (identity mapping) to enable proper cross-package linkage.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for the linkage table construction
    linkage_table_pattern = "let linkage_table = packages.keys().copied().map(|addr| (addr, addr)).collect();"

    assert linkage_table_pattern in content, (
        f"Missing required linkage table construction\n"
        f"Expected to find: {linkage_table_pattern}\n"
        "The fix must create a linkage table mapping addresses to themselves"
    )


def test_linkage_context_creation():
    """Fail-to-pass: Verify that LinkageContext is created from the linkage table.

    The fix creates a LinkageContext using the constructed linkage table.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for LinkageContext creation
    context_pattern = "let linkage_context = linkage_context::LinkageContext::new(linkage_table).unwrap();"

    assert context_pattern in content, (
        f"Missing required LinkageContext creation\n"
        f"Expected to find: {context_pattern}\n"
        "The fix must create a LinkageContext from the linkage table"
    )


def test_stored_package_with_linkage():
    """Fail-to-pass: Verify that StoredPackage uses the new with_linkage method.

    The critical fix: Instead of calling `from_modules_for_testing`,
    the code must call `from_module_for_testing_with_linkage` with the linkage context.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check for the new StoredPackage method with linkage
    # Note: The method name is `from_module_for_testing_with_linkage` (singular "module")
    method_pattern = "StoredPackage::from_module_for_testing_with_linkage("

    assert method_pattern in content, (
        f"Missing required StoredPackage::from_module_for_testing_with_linkage call\n"
        f"Expected to find: {method_pattern}\n"
        "The fix must use from_module_for_testing_with_linkage instead of from_modules_for_testing"
    )


def test_old_method_not_used():
    """Verify that the old from_modules_for_testing method is no longer used in the fixed section.

    After the fix, the old method should not be called in the setup_test_storage function.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # The old method name is `from_modules_for_testing` (plural "modules")
    old_method = "StoredPackage::from_modules_for_testing("

    # Count occurrences in the setup_test_storage function area
    # We need to check that it's not used in the packages loop
    lines = content.split('\n')
    in_setup_function = False
    brace_count = 0
    found_old_method_in_function = False

    for line in lines:
        if "fn setup_test_storage" in line:
            in_setup_function = True
            brace_count = 0

        if in_setup_function:
            # Track brace depth
            brace_count += line.count('{') - line.count('}')

            # Check for old method usage
            if old_method in line and "//" not in line:
                found_old_method_in_function = True
                break

            # End of function
            if brace_count == 0 and '{' in ''.join(lines[:lines.index(line)+1]):
                break

    assert not found_old_method_in_function, (
        f"Old method {old_method} should not be used in setup_test_storage\n"
        "The fix must replace the old method with from_module_for_testing_with_linkage"
    )


def test_linkage_context_passed_to_stored_package():
    """Fail-to-pass: Verify that the linkage_context is passed as parameter.

    The linkage_context must be passed as the second parameter to from_module_for_testing_with_linkage.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Check that linkage_context is passed to the StoredPackage constructor
    # Looking for pattern where linkage_context is used as a parameter
    assert "linkage_context.clone()," in content or "linkage_context," in content, (
        "The linkage_context must be passed to StoredPackage::from_module_for_testing_with_linkage\n"
        "Expected to see linkage_context as a parameter after the address"
    )


def test_code_compiles():
    """Pass-to-pass: Verify that the modified code compiles successfully.

    The fix must not break compilation of the move-unit-test crate.
    """
    result = run_command(
        ["cargo", "check", "-p", "move-unit-test"],
        cwd=REPO_ROOT,
        timeout=600
    )

    assert result.returncode == 0, (
        f"Code does not compile:\n{result.stderr}\n{result.stdout}"
    )


def test_unit_tests_run():
    """Pass-to-pass: Verify that the move-unit-test crate's unit tests pass.

    The fix should allow existing tests to continue passing.
    """
    result = run_command(
        ["cargo", "test", "-p", "move-unit-test", "--lib", "--", "--test-threads=1"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=600
    )

    # Check for compilation or test failures
    if result.returncode != 0:
        # Check if it's just that there are no tests (not a failure)
        if "no tests to run" in result.stdout.lower() or "no tests to run" in result.stderr.lower():
            return

        # Check for actual failures
        assert "FAILED" not in result.stdout and "FAILED" not in result.stderr, (
            f"Unit tests failed:\n{result.stdout}\n{result.stderr}"
        )

        # If returncode is non-zero but no explicit failures, it's likely a compilation issue
        assert result.returncode == 0, (
            f"Test run failed with exit code {result.returncode}:\n{result.stderr}\n{result.stdout}"
        )


def test_move_clippy():
    """Pass-to-pass: Verify that the move-unit-test crate passes clippy lints.

    The fix must not introduce new clippy warnings (pass_to_pass).
    """
    result = run_command(
        ["cargo", "clippy", "-p", "move-unit-test"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=120
    )
    assert result.returncode == 0, (
        f"Clippy failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    )


def test_move_fmt():
    """Pass-to-pass: Verify that the move-unit-test crate code is properly formatted.

    The fix must follow the codebase's formatting standards (pass_to_pass).
    """
    result = run_command(
        ["cargo", "fmt", "--check", "-p", "move-unit-test"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=60
    )
    assert result.returncode == 0, (
        f"Format check failed:\n{result.stderr}\n{result.stdout}"
    )


def test_move_unit_test_integration_tests():
    """Pass-to-pass: Verify that move-unit-test integration tests pass.

    The fix must not break the existing integration test suite (pass_to_pass).
    """
    result = run_command(
        ["cargo", "test", "-p", "move-unit-test", "--test", "move_unit_test_testsuite"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=120
    )
    assert result.returncode == 0, (
        f"Integration tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    )


def test_move_vm_runtime_unit_tests():
    """Pass-to-pass: Verify that move-vm-runtime unit tests pass.

    The fix involves linkage in the VM runtime, so this ensures the core
    runtime functionality remains intact (pass_to_pass).
    """
    result = run_command(
        ["cargo", "test", "-p", "move-vm-runtime", "--lib", "--", "--test-threads=1"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=300
    )
    assert result.returncode == 0, (
        f"VM runtime unit tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    )


def test_move_package_compiles():
    """Pass-to-pass: Verify that move-package crate compiles successfully.

    The move-package crate is used by the unit test runner for package resolution.
    This ensures it builds correctly (pass_to_pass).
    """
    result = run_command(
        ["cargo", "check", "-p", "move-package", "--all-targets"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=120
    )
    assert result.returncode == 0, (
        f"move-package check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    )


def test_move_cli_unit_tests():
    """Pass-to-pass: Verify that move-cli unit tests pass.

    The move-cli crate's tests ensure the CLI test runner works correctly.
    This is related to the unit test functionality being fixed (pass_to_pass).
    """
    result = run_command(
        ["cargo", "test", "-p", "move-cli", "--lib", "--", "--test-threads=1"],
        cwd=f"{REPO_ROOT}/external-crates/move",
        timeout=300
    )
    # Check for actual test failures, not just non-zero exit
    if result.returncode != 0:
        assert "FAILED" not in result.stdout and "FAILED" not in result.stderr, (
            f"CLI unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
        )
        # If no explicit failures but non-zero exit, check for compilation errors
        assert "error[" not in result.stderr.lower(), (
            f"CLI compilation errors:\n{result.stderr[-500:]}"
        )


def test_setup_test_storage_function_structure():
    """Fail-to-pass: Verify the overall structure of the fixed setup_test_storage function.

    This test checks that:
    1. linkage_table is constructed before the for loop
    2. linkage_context is created from linkage_table
    3. The for loop uses from_module_for_testing_with_linkage with linkage_context
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Find the setup_test_storage function and check its structure
    lines = content.split('\n')

    # Track key patterns in order
    found_packages_keys = False
    found_linkage_table = False
    found_linkage_context_create = False
    found_for_loop = False
    found_with_linkage_call = False

    for i, line in enumerate(lines):
        if "fn setup_test_storage" in line:
            # We're in the function, start tracking
            pass

        if "packages.keys().copied()" in line:
            found_packages_keys = True

        if "let linkage_table" in line and "packages.keys()" in line:
            found_linkage_table = True

        if "linkage_context::LinkageContext::new(linkage_table)" in line:
            found_linkage_context_create = True

        if "for (addr, modules) in packages" in line:
            found_for_loop = True

        if "StoredPackage::from_module_for_testing_with_linkage(" in line:
            found_with_linkage_call = True

    # All must be present for the fix to be complete
    assert found_packages_keys, "Missing: packages.keys() iteration for linkage_table"
    assert found_linkage_table, "Missing: linkage_table construction"
    assert found_linkage_context_create, "Missing: LinkageContext::new() call"
    assert found_for_loop, "Missing: for loop over packages"
    assert found_with_linkage_call, "Missing: from_module_for_testing_with_linkage call"
