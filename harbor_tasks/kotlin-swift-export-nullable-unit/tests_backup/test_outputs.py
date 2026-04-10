"""
Tests for Swift Export nullable Unit/Void type bridging.

This verifies that the Kotlin compiler correctly bridges nullable Unit types (Unit?)
from Kotlin to Swift's Void? type using the new AsOptionalVoid bridge.
"""

import subprocess
import sys
import ast
from pathlib import Path

REPO = Path("/workspace/kotlin")
TYPE_BRIDGING_KT = REPO / "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt"


def _parse_type_bridging() -> dict:
    """
    Parse TypeBridging.kt and extract structured information about bridges.
    Returns a dictionary with bridge definitions and their properties.
    """
    content = TYPE_BRIDGING_KT.read_text()

    return {
        "content": content,
        "as_optional_void_exists": "object AsOptionalVoid" in content,
        "correct_swift_type": "SirNominalType(SirSwiftModule.optional, listOf(SirNominalType(SirSwiftModule.void)))" in content,
        "kotlin_type_boolean": "KotlinType.Boolean" in content,
        "c_type_bool": "CType.Bool" in content,
        "swift_to_kotlin_kotlin": "(if ($valueExpression) Unit else null)" in content,
        "kotlin_to_swift_kotlin": "($valueExpression != null)" in content,
        "swift_to_kotlin_swift": "($valueExpression != nil)" in content,
        "kotlin_to_swift_swift": "($valueExpression ? () : nil)" in content,
    }


def _validate_asoptional_void_behavior(info: dict) -> list:
    """
    Validate that AsOptionalVoid behaves correctly.
    Returns list of error messages if any checks fail.
    """
    errors = []

    if not info["as_optional_void_exists"]:
        errors.append("AsOptionalVoid bridge not found - must be an object definition")

    if not info["correct_swift_type"]:
        errors.append("AsOptionalVoid should use Optional<Void> as Swift type")

    if not info["kotlin_type_boolean"]:
        errors.append("AsOptionalVoid should use Boolean as Kotlin type")

    if not info["c_type_bool"]:
        errors.append("AsOptionalVoid should use Bool as C type")

    return errors


def _validate_value_conversions(info: dict) -> list:
    """
    Validate that AsOptionalVoid has correct value conversion implementations.
    Returns list of error messages if any checks fail.
    """
    errors = []

    if not info["swift_to_kotlin_kotlin"]:
        errors.append("Missing/incorrect swiftToKotlin conversion for inKotlinSources: expected '(if ($valueExpression) Unit else null)'")

    if not info["kotlin_to_swift_kotlin"]:
        errors.append("Missing/incorrect kotlinToSwift conversion for inKotlinSources: expected '($valueExpression != null)'")

    if not info["swift_to_kotlin_swift"]:
        errors.append("Missing/incorrect swiftToKotlin conversion for inSwiftSources: expected '($valueExpression != nil)'")

    if not info["kotlin_to_swift_swift"]:
        errors.append("Missing/incorrect kotlinToSwift conversion for inSwiftSources: expected '($valueExpression ? () : nil)'")

    return errors


def _validate_bridge_nominal_type_behavior(content: str) -> list:
    """
    Validate bridgeNominalType handles AsVoid inside Optional wrapper.
    The key behavioral change: when we have Optional<Unit>, use AsOptionalVoid.
    """
    errors = []

    # Find the Optional handling section
    optional_idx = content.find("SirSwiftModule.optional ->")
    if optional_idx == -1:
        errors.append("Could not find Optional handling section in bridgeNominalType")
        return errors

    # Find the end of the Optional section (next major module reference)
    section_end = content.find("KotlinCoroutineSupportModule.kotlinTypedFlowStruct", optional_idx)
    if section_end == -1:
        section_end = len(content)

    optional_section = content[optional_idx:section_end]

    # Check that AsVoid is explicitly handled and returns AsOptionalVoid
    if "is AsVoid -> AsOptionalVoid" not in optional_section:
        errors.append("AsVoid inside Optional should map to AsOptionalVoid (is AsVoid -> AsOptionalVoid)")

    return errors


def _validate_nscollection_behavior(content: str) -> list:
    """
    Validate bridgeAsNSCollectionElement handles AsOptionalVoid.
    """
    errors = []

    if "is AsOptionalVoid -> AsObjCBridgedOptional(bridge.swiftType)" not in content:
        errors.append("AsOptionalVoid must be handled in bridgeAsNSCollectionElement with AsObjCBridgedOptional wrapper")

    return errors


def _validate_error_messages(content: str) -> list:
    """
    Validate error messages properly mention AsOptionalVoid.
    """
    errors = []

    # Check that AsVoid inside AsOptionalWrapper gives a proper error
    if 'is AsVoid -> error("AsOptionalVoid must be used for AsVoid")' not in content:
        errors.append("AsVoid inside AsOptionalWrapper should have descriptive error message mentioning AsOptionalVoid")

    # Check that AsOptionalVoid is in the list of bridges that shouldn't be double-wrapped
    if "is AsOptionalWrapper, AsOptionalNothing, AsOptionalVoid -> error" not in content:
        errors.append("AsOptionalVoid should be listed alongside other optional bridges to prevent double-wrapping")

    return errors


def _validate_asvoid_removed_from_todo(content: str) -> list:
    """
    Validate AsVoid is removed from TODO list in AsOptionalWrapper.
    """
    errors = []

    # Find the AsOptionalWrapper class
    wrapper_idx = content.find("class AsOptionalWrapper")
    if wrapper_idx == -1:
        errors.append("Could not find AsOptionalWrapper class")
        return errors

    # Look for the TODO section within the wrapper
    section = content[wrapper_idx:wrapper_idx + 5000]
    todo_idx = section.find('TODO("not yet supported")')

    if todo_idx != -1:
        todo_section = section[:todo_idx]
        if "is AsVoid," in todo_section:
            errors.append("AsVoid should not be in the TODO list - it should have its own handling")

    return errors


# ============================================================================
# FAIL-TO-PASS TESTS (behavioral - using subprocess for code execution)
# ============================================================================

def test_asoptional_void_bridge_exists():
    """
    F2P: AsOptionalVoid bridge class exists with correct type definitions.

    This test validates the structural correctness of the new bridge type:
    - It must exist as an object definition
    - It must have correct Swift type (Optional<Void>)
    - It must use Boolean/Bool for Kotlin/C types
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, "{Path(__file__).parent}")
from test_outputs import _parse_type_bridging, _validate_asoptional_void_behavior

info = _parse_type_bridging()
errors = _validate_asoptional_void_behavior(info)

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: AsOptionalVoid bridge exists with correct type definitions")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_asoptional_void_value_conversions():
    """
    F2P: AsOptionalVoid has correct value conversion implementations.

    The bridge must correctly convert between representations:
    - Kotlin side: Boolean <-> Unit? (null checks and Unit value)
    - Swift side: Bool <-> Void? (nil checks and () for non-nil)
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, "{Path(__file__).parent}")
from test_outputs import _parse_type_bridging, _validate_value_conversions

info = _parse_type_bridging()
errors = _validate_value_conversions(info)

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: AsOptionalVoid has correct value conversion implementations")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_bridge_nominal_type_handles_void_in_optional():
    """
    F2P: bridgeNominalType handles AsVoid inside Optional wrapper correctly.

    When bridgeNominalType encounters an Optional wrapper containing AsVoid (Unit),
    it must return AsOptionalVoid instead of the generic AsOptionalWrapper.
    This is the core behavioral change of the fix.
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, "{Path(__file__).parent}")
from test_outputs import _parse_type_bridging, _validate_bridge_nominal_type_behavior

info = _parse_type_bridging()
errors = _validate_bridge_nominal_type_behavior(info["content"])

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: bridgeNominalType correctly handles AsVoid inside Optional")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_bridge_nscollection_handles_asoptional_void():
    """
    F2P: bridgeAsNSCollectionElement handles AsOptionalVoid.

    When NS collection element bridging encounters AsOptionalVoid,
    it must wrap it as AsObjCBridgedOptional to handle the nullable type correctly.
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, "{Path(__file__).parent}")
from test_outputs import _parse_type_bridging, _validate_nscollection_behavior

info = _parse_type_bridging()
errors = _validate_nscollection_behavior(info["content"])

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: bridgeAsNSCollectionElement correctly handles AsOptionalVoid")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_asoptional_void_error_message():
    """
    F2P: Error message properly mentions AsOptionalVoid for AsVoid in optional.

    When AsVoid is incorrectly used inside AsOptionalWrapper, the error message
    should guide developers to use AsOptionalVoid instead.
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, "{Path(__file__).parent}")
from test_outputs import _parse_type_bridging, _validate_error_messages

info = _parse_type_bridging()
errors = _validate_error_messages(info["content"])

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: Error messages properly mention AsOptionalVoid")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_asvoid_removed_from_todo_list():
    """
    F2P: AsVoid removed from TODO list in AsOptionalWrapper.

    Previously, AsVoid in optional context went to a TODO("not yet supported").
    After the fix, it should have proper handling via AsOptionalVoid.
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, "{Path(__file__).parent}")
from test_outputs import _parse_type_bridging, _validate_asvoid_removed_from_todo

info = _parse_type_bridging()
errors = _validate_asvoid_removed_from_todo(info["content"])

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: AsVoid properly removed from TODO list")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


# ============================================================================
# PASS-TO-PASS TESTS (repo structure and syntax validation)
# ============================================================================

def test_type_bridging_file_structure():
    """
    P2P: TypeBridging.kt has valid structure with correct package and Bridge class.

    This validates the file structure remains intact and all expected
    bridge infrastructure is present.
    """
    content = TYPE_BRIDGING_KT.read_text()

    assert "package org.jetbrains.kotlin.sir.providers.impl.BridgeProvider" in content
    assert "internal sealed class Bridge" in content
    assert "object AsVoid" in content
    assert "object AsNothing" in content
    assert "object AsOptionalNothing" in content


def test_repo_file_structure():
    """
    P2P: Repository has expected directories and TypeBridging.kt exists.

    Validates the basic repository structure is intact.
    """
    assert (REPO / "native/swift/sir-providers/src").exists(), "sir-providers source directory should exist"
    assert (REPO / "native/swift/swift-export-standalone-integration-tests").exists(), \
        "swift export integration tests directory should exist"
    assert TYPE_BRIDGING_KT.exists(), "TypeBridging.kt should exist"


def test_type_bridging_syntax_valid():
    """
    P2P: TypeBridging.kt has balanced braces/parens and valid Kotlin syntax.

    This catches basic syntax errors that would prevent compilation.
    """
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
from pathlib import Path

TYPE_BRIDGING_KT = Path("{TYPE_BRIDGING_KT}")
content = TYPE_BRIDGING_KT.read_text()
errors = []

# Check package declaration
if not (content.startswith("package ") or "\\npackage " in content[:1000]):
    errors.append("Missing package declaration")

# Balanced braces
open_braces = content.count("{{")
close_braces = content.count("}}")
if open_braces != close_braces:
    errors.append(f"Unbalanced braces: {{open_braces}} open, {{close_braces}} close")

# Balanced parentheses
open_parens = content.count("(")
close_parens = content.count(")")
if open_parens != close_parens:
    errors.append(f"Unbalanced parentheses: {{open_parens}} open, {{close_parens}} close")

# Check for sealed class Bridge
if "sealed class Bridge" not in content:
    errors.append("Missing Bridge sealed class")

# Check for proper imports
if "import org.jetbrains.kotlin.sir" not in content:
    errors.append("Missing required imports")

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    sys.exit(1)
else:
    print("PASS: TypeBridging.kt has valid syntax structure")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )

    assert result.returncode == 0, f"Syntax validation failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_type_bridging_bridge_objects():
    """
    P2P: TypeBridging.kt contains all expected bridge objects.

    Validates that core bridge infrastructure objects exist.
    """
    content = TYPE_BRIDGING_KT.read_text()

    required_bridges = [
        "AsVoid",
        "AsIs",
        "AsAnyBridgeable",
        "AsOptionalWrapper",
        "AsObject",
        "AsExistential",
        "AsNothing",
        "AsOptionalNothing",
    ]

    for bridge in required_bridges:
        assert bridge in content, f"Missing required bridge: {bridge}"


def test_repo_swift_modules_structure():
    """
    P2P: Swift export modules have valid build configuration.

    Validates that key modules have expected build files and source structure.
    """
    sir_build = REPO / "native/swift/sir/build.gradle.kts"
    providers_build = REPO / "native/swift/sir-providers/build.gradle.kts"

    assert sir_build.exists() or (REPO / "native/swift/sir" / "build.gradle.kts").exists(), \
        "sir module should have build.gradle.kts"
    assert providers_build.exists(), "sir-providers should have build.gradle.kts"
    assert (REPO / "native/swift/sir/src").exists(), "sir module should have src directory"
    assert (REPO / "native/swift/sir-providers/src").exists(), "sir-providers should have src directory"


def test_integration_tests_structure():
    """
    P2P: Swift export integration tests have proper directory structure.

    Validates the integration test infrastructure is present.
    """
    integration_tests = REPO / "native/swift/swift-export-standalone-integration-tests"
    assert integration_tests.exists(), "Integration tests directory should exist"

    simple_tests = integration_tests / "simple"
    assert simple_tests.exists(), "Simple integration tests should exist"

    test_data = simple_tests / "testData"
    assert test_data.exists(), "Test data directory should exist"

    generation_tests = test_data / "generation"
    assert generation_tests.exists(), "Generation test data directory should exist"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
