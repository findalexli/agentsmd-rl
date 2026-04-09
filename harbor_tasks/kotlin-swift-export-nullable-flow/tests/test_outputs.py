"""
Test outputs for Kotlin Swift Export nullable Flow support.

This tests that the fix for nullable elements in Kotlin Flow when exported
to Swift is properly implemented.
"""

import re
import os

REPO = "/workspace/kotlin"

# File paths
KOTLIN_SUPPORT_KT = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt"
KOTLIN_SUPPORT_SWIFT = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"
KOTLIN_SUPPORT_H = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h"
TEST_KT = "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt"
TEST_SWIFT = "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift"


def test_header_has_bool_parameter():
    """
    Check that KotlinCoroutineSupport.h has the updated signature with bool parameter.
    The callback now takes (bool, void*) instead of just (void*).
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_H), 'r') as f:
        content = f.read()

    # Check for the new signature with bool parameter
    pattern = r'_kotlin_swift_SwiftFlowIterator_next.*bool.*void \* _Nullable'
    match = re.search(pattern, content)
    assert match is not None, \
        "Header file missing updated signature with bool parameter for nullable support"


def test_kt_has_value_wrapper_class():
    """
    Check that KotlinCoroutineSupport.kt has the inner Value wrapper class.
    This class is used to distinguish null values from completion.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check for the inner Value class
    assert "inner class Value(val value: T)" in content, \
        "Kotlin file missing inner Value wrapper class"


def test_kt_next_returns_value_type():
    """
    Check that the next() function returns Value? instead of T?.
    This is key to distinguishing null values from completion.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Look for the next() function signature returning Value?
    pattern = r'public suspend fun next\(\): Value\?'
    match = re.search(pattern, content)
    assert match is not None, \
        "next() function should return Value? to distinguish null values from completion"


def test_kt_continuation_uses_value_wrapper():
    """
    Check that continuation.resume() wraps value in Value class.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check that continuation.resume wraps value
    assert "state.continuation.resume(Value(value))" in content, \
        "Continuation should wrap value in Value class"


def test_kt_callback_has_bool_and_value():
    """
    Check that SwiftFlowIterator_next has updated callback with (Boolean, NativePtr).
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check for the callback signature change
    pattern = r'convertBlockPtrToKotlinFunction<\(kotlin\.Boolean, kotlin\.native\.internal\.NativePtr\)->Unit>'
    match = re.search(pattern, content)
    assert match is not None, \
        "SwiftFlowIterator_next should have callback with (Boolean, NativePtr) parameters"


def test_kt_callback_passes_boolean_flag():
    """
    Check that the continuation callback properly passes boolean flag
    indicating if value is present or null.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check for the pattern where result is checked and proper boolean is passed
    assert '__continuation(false, null)' in content, \
        "Should call continuation with false when result is null (flow completed)"
    assert '__continuation(true, _result.value)' in content, \
        "Should call continuation with true and value when result is present"


def test_swift_callback_handles_bool():
    """
    Check that Swift code handles the boolean flag from the callback.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_SWIFT), 'r') as f:
        content = f.read()

    # Check for the callback handling with arg0 (bool) and arg1 (value)
    pattern = r'_kotlin_swift_SwiftFlowIterator_next.*\{ arg0, arg1 in'
    match = re.search(pattern, content)
    assert match is not None, \
        "Swift callback should have arg0 (bool) and arg1 (value) parameters"


def test_swift_handles_boolean_for_optional():
    """
    Check that Swift code uses boolean flag to determine .some vs .none.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_SWIFT), 'r') as f:
        content = f.read()

    # Check for proper handling of boolean flag
    assert 'if arg0 {' in content, \
        "Swift should check arg0 (bool) to determine if value is present"
    assert 'continuation(.some(element))' in content, \
        "Swift should pass .some(element) when value is present"
    assert 'continuation(.none)' in content, \
        "Swift should pass .none when value is null"


def test_kt_test_file_has_nullable_flow_function():
    """
    Check that test data has testNullable() function returning Flow<Elem?>.
    """
    with open(os.path.join(REPO, TEST_KT), 'r') as f:
        content = f.read()

    # Check for testNullable function with nullable element type
    pattern = r'fun testNullable\(\): Flow<Elem\?>'
    match = re.search(pattern, content)
    assert match is not None, \
        "Test file missing testNullable() function with nullable Elem type"


def test_swift_test_has_nullable_test():
    """
    Check that Swift test file has testNullable() async test.
    """
    with open(os.path.join(REPO, TEST_SWIFT), 'r') as f:
        content = f.read()

    # Check for testNullable function
    assert "func testNullable() async" in content, \
        "Swift test file missing testNullable() function"


def test_swift_test_includes_null_in_expected():
    """
    Check that Swift test expects nil values in the result array.
    This is the key test that verifies nullable elements work.
    """
    with open(os.path.join(REPO, TEST_SWIFT), 'r') as f:
        content = f.read()

    # The test should expect nil values in the array
    # Pattern: [Element1.shared, nil, Element2.shared, nil, Element3.shared]
    pattern = r'\[Elem\?\] = \[.*nil.*nil.*\]'
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, \
        "Swift test should expect array with nil values for nullable flow test"
