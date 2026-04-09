"""Tests for Swift Export context parameters feature.

This test module verifies that the Kotlin Swift Export feature correctly handles
context parameters on functional types. The fix involves:

1. Adding contextTypes field to SirFunctionalType class
2. Updating SirAsSwiftSourcesPrinter to print context parameters
3. Updating type bridging to handle context parameters in function types
4. Updating SirTypeProviderImpl to extract context receivers from KaFunctionType
5. Updating StandaloneSirTypeNamer to include context types in Kotlin FqName
"""

import subprocess
import sys
import os

REPO = "/workspace/kotlin"


def test_sir_printer_compiles():
    """sir-printer module compiles successfully (pass_to_pass)."""
    result = subprocess.run(
        ["./gradlew", ":native:swift:sir-printer:compileKotlin", "-q", "--no-daemon"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900
    )
    assert result.returncode == 0, f"sir-printer compilation failed:\n{result.stderr[-1000:]}"


def test_sir_compiles():
    """sir module compiles successfully (pass_to_pass)."""
    result = subprocess.run(
        ["./gradlew", ":native:swift:sir:compileKotlin", "-q", "--no-daemon"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900
    )
    assert result.returncode == 0, f"sir compilation failed:\n{result.stderr[-1000:]}"


def test_sir_providers_compiles():
    """sir-providers module compiles successfully (pass_to_pass)."""
    result = subprocess.run(
        ["./gradlew", ":native:swift:sir-providers:compileKotlin", "-q", "--no-daemon"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900
    )
    assert result.returncode == 0, f"sir-providers compilation failed:\n{result.stderr[-1000:]}"


def test_sir_functional_type_has_context_types():
    """SirFunctionalType has contextTypes field (fail_to_pass).

    This test verifies that SirFunctionalType class includes the contextTypes field
    which is essential for supporting context parameters on functional types.
    """
    # Read the SirType.kt file and check for contextTypes field
    sir_type_file = os.path.join(REPO, "native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt")
    with open(sir_type_file, 'r') as f:
        content = f.read()

    # Check for contextTypes parameter in constructor
    assert "val contextTypes: List<SirType>" in content, \
        "SirFunctionalType missing contextTypes field"

    # Check for contextType computed property
    assert "val contextType: SirType?" in content, \
        "SirFunctionalType missing contextType computed property"

    # Check that copyAppendingAttributes includes contextTypes
    assert "SirFunctionalType(contextTypes, parameterTypes" in content, \
        "copyAppendingAttributes does not preserve contextTypes"


def test_sir_functional_type_equals_hashcode():
    """SirFunctionalType has proper equals and hashCode (fail_to_pass).

    Since contextTypes was added as a new field, equals and hashCode must
    include it to maintain correct behavior.
    """
    sir_type_file = os.path.join(REPO, "native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt")
    with open(sir_type_file, 'r') as f:
        content = f.read()

    # Check for equals method including contextTypes
    assert "if (contextTypes != other.contextTypes) return false" in content, \
        "equals() does not compare contextTypes"

    # Check for hashCode including contextTypes
    assert "var result = contextTypes.hashCode()" in content, \
        "hashCode() does not include contextTypes"


def test_printer_includes_context_type():
    """SirAsSwiftSourcesPrinter includes contextType in functional types (fail_to_pass).

    The printer must render context parameters before regular parameters when
    printing functional types.
    """
    printer_file = os.path.join(
        REPO,
        "native/swift/sir-printer/src/org/jetbrains/sir/printer/impl/SirAsSwiftSourcesPrinter.kt"
    )
    with open(printer_file, 'r') as f:
        content = f.read()

    # Check that the printer uses contextType when rendering parameters
    assert "(listOfNotNull(contextType) + parameterTypes).render()" in content, \
        "Printer does not include contextType in functional type rendering"


def test_type_provider_extracts_context_receivers():
    """SirTypeProviderImpl extracts context receivers from KaFunctionType (fail_to_pass).

    The type provider must translate Kotlin context receivers into Swift context types.
    """
    provider_file = os.path.join(
        REPO,
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt"
    )
    with open(provider_file, 'r') as f:
        content = f.read()

    # Check for KaExperimentalApi import
    assert "import org.jetbrains.kotlin.analysis.api.KaExperimentalApi" in content, \
        "Missing KaExperimentalApi import"

    # Check that contextReceivers are being mapped
    assert "contextTypes = kaType.contextReceivers.map" in content, \
        "TypeProvider does not extract contextReceivers"


def test_type_namer_includes_context_types():
    """StandaloneSirTypeNamer includes context types in Kotlin FqName (fail_to_pass).

    The function arity and type arguments must include context types.
    """
    namer_file = os.path.join(
        REPO,
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt"
    )
    with open(namer_file, 'r') as f:
        content = f.read()

    # Check that function arity includes contextTypes count
    assert "type.contextTypes.count() + type.parameterTypes.count()" in content, \
        "TypeNamer does not include contextTypes in function arity"

    # Check that type arguments include context types
    assert "(type.contextTypes + type.parameterTypes + type.returnType)" in content, \
        "TypeNamer does not include contextTypes in type arguments"


def test_type_bridging_handles_context_parameters():
    """TypeBridging handles context parameters in AsContravariantBlock (fail_to_pass).

    The bridge implementation must handle context parameters when generating
    Kotlin-to-Swift and Swift-to-Kotlin conversions.
    """
    bridging_file = os.path.join(
        REPO,
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt"
    )
    with open(bridging_file, 'r') as f:
        content = f.read()

    # Check for contextParameters field in AsContravariantBlock
    assert "private val contextParameters: List<KotlinToSwiftBridge>" in content, \
        "AsContravariantBlock missing contextParameters field"

    # Check that contextTypes are bridged
    assert "contextParameters = swiftType.contextTypes.map { bridgeReturnType(it) }" in content, \
        "TypeBridging does not bridge contextTypes"

    # Check for ctx variable naming in closure
    assert '"ctx${idx}" to el' in content, \
        "TypeBridging does not use ctx naming for context parameters"


def test_sir_printer_tests_pass():
    """sir-printer tests pass including new context parameter tests (fail_to_pass).

    This runs the actual test suite for sir-printer to verify the fix works
    correctly in practice.
    """
    result = subprocess.run(
        ["./gradlew", ":native:swift:sir-printer:test", "-q", "--no-daemon", "--parallel"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=1200
    )
    assert result.returncode == 0, f"sir-printer tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
