#!/usr/bin/env python3
"""Test outputs for Swift Export Flow nullable elements fix."""

import subprocess
import sys
from pathlib import Path
import pytest

REPO = Path("/workspace/kotlin")
RESOURCES = REPO / "native/swift/swift-export-standalone/resources/swift"
KOTLIN_SUPPORT = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt"
C_HEADER = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h"
SWIFT_SUPPORT = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"


def read_file(path: Path) -> str:
    """Read file contents or fail test."""
    if not path.exists():
        pytest.fail(f"File not found: {path}")
    return path.read_text()


def test_value_wrapper_class_exists():
    """FAIL-TO-PASS: SwiftFlowIterator has inner Value wrapper class."""
    content = read_file(KOTLIN_SUPPORT)

    # Check for inner class Value definition
    assert "inner class Value(val value: T)" in content, \
        "Missing inner class Value wrapper - needed to distinguish null values from end-of-flow"


def test_next_function_returns_value_type():
    """FAIL-TO-PASS: next() returns Value? instead of T? to properly wrap nullable values."""
    content = read_file(KOTLIN_SUPPORT)

    # The suspend fun next() should return Value? not T?
    assert "public suspend fun next(): Value?" in content, \
        "next() should return Value? to wrap nullable elements - returning T? cannot distinguish null value from end"


def test_emit_uses_value_wrapper():
    """FAIL-TO-PASS: emit() wraps values in Value class before resuming continuation."""
    content = read_file(KOTLIN_SUPPORT)

    # In emit(), values should be wrapped in Value before resuming
    assert "state.continuation.resume(Value(value))" in content, \
        "emit() must wrap value in Value() wrapper before resuming continuation"


def test_handleactions_uses_value_type():
    """FAIL-TO-PASS: handleActions uses Value type for consumer await."""
    content = read_file(KOTLIN_SUPPORT)

    # Count occurrences of handleActions<Value> - should be at least 2 (for Ready and AwaitingConsumer states)
    count = content.count("handleActions<Value>")
    assert count >= 2, \
        f"Expected at least 2 handleActions<Value> calls, found {count} - needed for state machine value handling"


def test_c_header_bool_parameter():
    """FAIL-TO-PASS: C header callback takes bool parameter for nullability flag."""
    content = read_file(C_HEADER)

    # The continuation callback should have bool parameter
    assert "int32_t (^continuation)(bool, void * _Nullable )" in content, \
        "C header continuation callback must have bool parameter to indicate nullability"


def test_kotlin_bridge_two_args():
    """FAIL-TO-PASS: Kotlin bridge function passes two arguments (bool flag + value)."""
    content = read_file(KOTLIN_SUPPORT)

    # The SwiftFlowIterator_next function should pass two arguments
    assert "__continuation(arg0, arg1)" in content or "__continuation(false, null)" in content, \
        "Kotlin bridge must pass boolean flag and value as separate arguments"

    # Check that null case passes false
    assert '__continuation(false, null)' in content, \
        "When result is null (end of flow), should call continuation(false, null)"

    # Check that value case passes true
    assert '__continuation(true, _result.value)' in content, \
        "When result has value, should call continuation(true, _result.value)"


def test_swift_handles_bool_flag():
    """FAIL-TO-PASS: Swift code checks boolean flag before unwrapping value."""
    content = read_file(SWIFT_SUPPORT)

    # Swift should check arg0 (the bool flag) before unwrapping
    assert "if arg0 {" in content, \
        "Swift code must check arg0 boolean flag before unwrapping value"

    # Swift should call continuation with .some(element) when flag is true
    assert "continuation(.some(element))" in content, \
        "Swift should pass non-nil value via continuation(.some(element)) when flag is true"

    # Swift should call continuation with .none when flag is false
    assert "continuation(.none)" in content, \
        "Swift should pass nil via continuation(.none) when flag is false"


def test_swift_callback_signature():
    """FAIL-TO-PASS: Swift callback closure accepts two arguments."""
    content = read_file(SWIFT_SUPPORT)

    # The callback to _kotlin_swift_SwiftFlowIterator_next should take 2 args
    assert "{ arg0, arg1 in" in content, \
        "Swift callback closure must accept two arguments (bool flag and value)"


def test_kotlin_function_signature():
    """FAIL-TO-PASS: Kotlin function type in bridge has boolean parameter."""
    content = read_file(KOTLIN_SUPPORT)

    # The convertBlockPtrToKotlinFunction type should include Boolean
    assert "convertBlockPtrToKotlinFunction<(kotlin.Boolean, kotlin.native.internal.NativePtr)->Unit>" in content, \
        "Kotlin function type must include Boolean as first parameter"


def test_swift_format_syntax():
    """PASS-TO-PASS: Swift files have valid syntax (swift-format returns exit 0)."""
    r = subprocess.run(
        ["bash", "-lc", f"swift-format lint KotlinCoroutineSupport.swift"],
        capture_output=True, text=True, timeout=60, cwd=str(RESOURCES)
    )
    assert r.returncode == 0, f"swift-format lint failed:\n{r.stderr[-500:]}"


def test_header_file_valid():
    """PASS-TO-PASS: C header file exists and has valid structure."""
    content = read_file(C_HEADER)
    # Verify this is a valid Objective-C/C header with expected markers
    assert "#include <Foundation/Foundation.h>" in content, "Missing Foundation.h include"
    assert "NS_ASSUME_NONNULL_BEGIN" in content, "Missing NS_ASSUME_NONNULL_BEGIN"
    assert "NS_ASSUME_NONNULL_END" in content, "Missing NS_ASSUME_NONNULL_END"


def test_repo_structure():
    """PASS-TO-PASS: Required resource files exist in expected locations."""
    # Verify all target files exist at the base commit
    required_files = [
        RESOURCES / "KotlinCoroutineSupport.kt",
        RESOURCES / "KotlinCoroutineSupport.swift",
        RESOURCES / "KotlinCoroutineSupport.h",
        REPO / "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt",
        REPO / "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift",
    ]
    missing = [f for f in required_files if not f.exists()]
    assert not missing, f"Missing required files: {missing}"


def test_kotlin_test_nullable_flow():
    """FAIL-TO-PASS: Kotlin test data includes nullable flow emitting interleaved nulls."""
    sequences_kt = REPO / "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt"
    content = read_file(sequences_kt)
    assert "fun testNullable(): Flow<Elem?> = flowOf(Element1, null, Element2, null, Element3)" in content, \
        "Must add nullable flow test returning Flow<Elem?> with interleaved null elements"


def test_swift_test_nullable_flow():
    """FAIL-TO-PASS: Swift test data collects nullable elements from async sequence."""
    sequences_swift = REPO / "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift"
    content = read_file(sequences_swift)
    assert "func testNullable()" in content, \
        "Must add testNullable() Swift test function"
    assert ".asAsyncSequence()" in content, \
        "Must consume the flow via asAsyncSequence() to verify nullable element handling"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
