"""
Tests for Swift Export Flow contravariant positions fix.

This verifies that Flow<T> types are properly handled in contravariant positions
(function parameters), not just covariant positions (return types).
"""

import subprocess
import os
import sys

REPO = "/workspace/kotlin"


def test_flow_handling_in_contravariant_position():
    """
    F2P: Flow type handling should not be restricted to covariant positions.

    The fix removes the `&& ctx.currentPosition == SirTypeVariance.COVARIANT` check
    so that Flow types are intercepted in all positions, including contravariant
    (function parameter) positions.
    """
    # Read the SirTypeProviderImpl.kt file
    file_path = os.path.join(REPO, "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt")
    with open(file_path, "r") as f:
        content = f.read()

    # Check that the fix is present: Flow class ID check without variance restriction
    # The fix removes: "&& ctx.currentPosition == SirTypeVariance.COVARIANT"
    # And keeps just: "if (kaType.classId in FLOW_CLASS_IDS)"

    # Look for the pattern where FLOW_CLASS_IDS check is NOT followed by variance check
    lines = content.split("\n")

    found_fixed_pattern = False
    found_broken_pattern = False

    for i, line in enumerate(lines):
        if "kaType.classId in FLOW_CLASS_IDS" in line:
            # Check the same line or next line for the variance restriction
            combined = line
            if i + 1 < len(lines):
                combined += lines[i + 1]

            if "SirTypeVariance.COVARIANT" in combined:
                found_broken_pattern = True
            else:
                found_fixed_pattern = True

    # The fix should be present (no variance restriction)
    assert found_fixed_pattern, "Flow type handling should not be restricted to covariant positions"
    assert not found_broken_pattern, "Found old pattern with variance restriction - fix not applied"


def test_companion_object_visibility():
    """
    F2P: Companion object in SirTypeProviderImpl should be internal for cross-file access.

    The fix changes `private companion object` to `internal companion object` so that
    FLOW_CLASS_IDS can be accessed from SirVisibilityCheckerImpl.
    """
    file_path = os.path.join(REPO, "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt")
    with open(file_path, "r") as f:
        content = f.read()

    # Check for internal companion object with FLOW_CLASS_ID definitions
    assert "internal companion object" in content, \
        "Companion object should be internal to allow cross-file access to FLOW_CLASS_IDS"

    # Verify FLOW_CLASS_ID constants are still present
    assert 'val FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/Flow")' in content, \
        "FLOW_CLASS_ID constant should be present"


def test_visibility_checker_flow_support():
    """
    F2P: SirVisibilityCheckerImpl should recognize Flow types as supported.

    The fix adds a check in hasUnboundInputTypeParameters to recognize Flow types
    as supported types, allowing them to be used in exported function signatures.
    """
    file_path = os.path.join(REPO, "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt")
    with open(file_path, "r") as f:
        content = f.read()

    # Check that the fix is present: Flow class ID check in visibility checker
    assert "classType.classId in SirTypeProviderImpl.FLOW_CLASS_IDS" in content, \
        "SirVisibilityCheckerImpl should check for Flow types using SirTypeProviderImpl.FLOW_CLASS_IDS"


def test_gradle_module_exists():
    """
    P2P: The sir-providers module should exist.

    This ensures we're working in the correct repository structure.
    """
    build_file = os.path.join(REPO, "native/swift/sir-providers/build.gradle.kts")
    assert os.path.exists(build_file), f"sir-providers build file should exist at {build_file}"


def test_kotlin_file_syntax_valid():
    """
    P2P: The modified Kotlin files should have valid syntax.

    We verify this by checking for balanced braces and no obvious syntax errors.
    """
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt"
    ]

    for file_path in files_to_check:
        full_path = os.path.join(REPO, file_path)
        with open(full_path, "r") as f:
            content = f.read()

        # Check for basic syntax indicators
        # Count braces
        open_braces = content.count("{")
        close_braces = content.count("}")

        assert open_braces == close_braces, \
            f"Unbalanced braces in {file_path}: {open_braces} open, {close_braces} close"

        # Check for unclosed parentheses in function signatures (basic check)
        open_parens = content.count("(")
        close_parens = content.count(")")

        assert open_parens == close_parens, \
            f"Unbalanced parentheses in {file_path}: {open_parens} open, {close_parens} close"


def test_flow_types_not_unbound():
    """
    F2P: Flow types should not be treated as having unbound type parameters.

    Before the fix, Flow types in contravariant positions would be incorrectly
    flagged as having unbound input type parameters, preventing export.
    After the fix, they are recognized as supported types.
    """
    file_path = os.path.join(REPO, "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt")
    with open(file_path, "r") as f:
        content = f.read()

    # The fix adds a check that returns false (not unbound) for Flow types
    # Pattern: "if (classType.classId in SirTypeProviderImpl.FLOW_CLASS_IDS) return@let false"
    # This can be on one line or split across lines
    found_flow_check = False
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if "classType.classId in SirTypeProviderImpl.FLOW_CLASS_IDS" in line:
            # Check same line and next line for the return statement
            combined = line
            if i + 1 < len(lines):
                combined += " " + lines[i + 1]

            if "return@let false" in combined or "return false" in combined:
                found_flow_check = True
                break

    assert found_flow_check, \
        "Flow types should return false from hasUnboundInputTypeParameters, indicating they are supported"
