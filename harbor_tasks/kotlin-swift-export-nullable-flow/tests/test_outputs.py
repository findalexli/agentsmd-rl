"""
Test outputs for Kotlin Swift Export nullable Flow support.

This tests that the fix for nullable elements in Kotlin Flow when exported
to Swift is properly implemented.
"""

import re
import os
import subprocess

REPO = "/workspace/kotlin"

# File paths
KOTLIN_SUPPORT_KT = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt"
KOTLIN_SUPPORT_SWIFT = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"
KOTLIN_SUPPORT_H = "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h"
TEST_KT = "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt"
TEST_SWIFT = "native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift"


# ==============================================================================
# PASS_TO_PASS TESTS - Repo CI/CD Sanity Checks
# These tests verify that the existing repo functionality remains intact.
# They should pass both on the base commit AND after the gold fix.
# ==============================================================================


def test_p2p_kotlin_coroutine_files_exist():
    """
    Pass-to-pass: Verify all core Kotlin coroutine support files exist.
    """
    files = [
        KOTLIN_SUPPORT_KT,
        KOTLIN_SUPPORT_SWIFT,
        KOTLIN_SUPPORT_H,
    ]
    for f in files:
        path = os.path.join(REPO, f)
        assert os.path.exists(path), f"Required file missing: {f}"
        assert os.path.getsize(path) > 0, f"Required file is empty: {f}"


def test_p2p_header_has_valid_syntax():
    """
    Pass-to-pass: Header file has valid C-style syntax with proper guards.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_H), 'r') as f:
        content = f.read()

    # Check for NS_ASSUME_NONNULL_BEGIN/END pattern
    assert "NS_ASSUME_NONNULL_BEGIN" in content, "Header missing NS_ASSUME_NONNULL_BEGIN"
    assert "NS_ASSUME_NONNULL_END" in content, "Header missing NS_ASSUME_NONNULL_END"

    # Check for proper function declarations
    assert "_kotlin_swift_SwiftFlowIterator_cancel" in content, "Header missing SwiftFlowIterator_cancel"
    assert "_kotlin_swift_SwiftFlowIterator_next" in content, "Header missing SwiftFlowIterator_next"
    assert "_kotlin_swift_SwiftFlowIterator_init_allocate" in content, "Header missing SwiftFlowIterator_init_allocate"


def test_p2p_kotlin_has_swift_flow_iterator_class():
    """
    Pass-to-pass: Kotlin file has SwiftFlowIterator class with required methods.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check for SwiftFlowIterator class
    assert "class SwiftFlowIterator<T>" in content, "Kotlin file missing SwiftFlowIterator class"

    # Check for required methods
    assert "suspend fun next()" in content, "Kotlin file missing next() method"
    assert "fun cancel()" in content or "public fun cancel()" in content, "Kotlin file missing cancel() method"

    # Check for FlowCollector implementation
    assert "FlowCollector<T>" in content, "SwiftFlowIterator should implement FlowCollector"


def test_p2p_kotlin_has_swift_job_class():
    """
    Pass-to-pass: Kotlin file has SwiftJob class for cancellation support.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check for SwiftJob class
    assert "class SwiftJob" in content, "Kotlin file missing SwiftJob class"

    # Check for cancellation callback
    assert "cancellationCallback" in content, "SwiftJob missing cancellationCallback"


def test_p2p_swift_has_kotlin_flow_iterator():
    """
    Pass-to-pass: Swift file has KotlinFlowIterator class with AsyncIteratorProtocol.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_SWIFT), 'r') as f:
        content = f.read()

    # Check for KotlinFlowIterator class
    assert "class KotlinFlowIterator<Element>" in content or "public final class KotlinFlowIterator<Element>" in content, \
        "Swift file missing KotlinFlowIterator class"

    # Check for AsyncIteratorProtocol conformance
    assert "AsyncIteratorProtocol" in content, "KotlinFlowIterator should conform to AsyncIteratorProtocol"

    # Check for next() method
    assert "public func next()" in content, "Swift file missing next() method"


def test_p2p_swift_has_kotlin_flow_sequence():
    """
    Pass-to-pass: Swift file has KotlinFlowSequence with AsyncSequence conformance.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_SWIFT), 'r') as f:
        content = f.read()

    # Check for KotlinFlowSequence
    assert "struct KotlinFlowSequence<Element>" in content or "public struct KotlinFlowSequence<Element>" in content, \
        "Swift file missing KotlinFlowSequence"

    # Check for AsyncSequence conformance
    assert "AsyncSequence" in content, "KotlinFlowSequence should conform to AsyncSequence"

    # Check for makeAsyncIterator
    assert "makeAsyncIterator" in content, "Swift file missing makeAsyncIterator method"


def test_p2p_swift_has_kotlin_task():
    """
    Pass-to-pass: Swift file has KotlinTask class for job bridging.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_SWIFT), 'r') as f:
        content = f.read()

    # Check for KotlinTask
    assert "class KotlinTask" in content or "final class KotlinTask" in content, \
        "Swift file missing KotlinTask class"

    # Check for cancelExternally method
    assert "cancelExternally" in content, "Swift file missing cancelExternally method"


def test_p2p_test_data_files_exist():
    """
    Pass-to-pass: Test data files exist and have expected structure.
    """
    # Check Kotlin test data
    kt_path = os.path.join(REPO, TEST_KT)
    assert os.path.exists(kt_path), f"Kotlin test data file missing: {TEST_KT}"

    with open(kt_path, 'r') as f:
        kt_content = f.read()

    # Check for expected test functions
    assert "fun testRegular()" in kt_content, "Test data missing testRegular()"
    assert "fun testEmpty()" in kt_content, "Test data missing testEmpty()"
    assert "Flow<Elem>" in kt_content, "Test data missing Flow<Elem> usage"

    # Check Swift test data
    swift_path = os.path.join(REPO, TEST_SWIFT)
    assert os.path.exists(swift_path), f"Swift test data file missing: {TEST_SWIFT}"

    with open(swift_path, 'r') as f:
        swift_content = f.read()

    # Check for expected test functions
    assert "func testRegular()" in swift_content, "Swift test missing testRegular()"
    assert "func testEmpty()" in swift_content, "Swift test missing testEmpty()"


def test_p2p_header_swift_callback_signature_exists():
    """
    Pass-to-pass: Header has callback signature for SwiftFlowIterator_next.
    The base commit has (void *) signature which should be valid C.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_H), 'r') as f:
        content = f.read()

    # Check for the callback function pointer parameter in _kotlin_swift_SwiftFlowIterator_next
    # This should exist in both base and fixed versions
    assert "_kotlin_swift_SwiftFlowIterator_next" in content, "Header missing _kotlin_swift_SwiftFlowIterator_next"
    assert "continuation" in content, "Header missing continuation parameter"


def test_p2p_kotlin_exported_bridge_functions_exist():
    """
    Pass-to-pass: Kotlin file has required @ExportedBridge functions.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_KT), 'r') as f:
        content = f.read()

    # Check for exported bridge functions
    exported_bridges = [
        "_kotlin_swift_SwiftFlowIterator_init_allocate",
        "_kotlin_swift_SwiftFlowIterator_init_initialize",
        "SwiftFlowIterator_next",
        "SwiftFlowIterator_cancel",
    ]

    for bridge in exported_bridges:
        assert bridge in content, f"Kotlin file missing exported bridge: {bridge}"


def test_p2p_swift_imports_kotlin_runtime():
    """
    Pass-to-pass: Swift file imports required Kotlin runtime modules.
    """
    with open(os.path.join(REPO, KOTLIN_SUPPORT_SWIFT), 'r') as f:
        content = f.read()

    # Check for required imports
    assert "import KotlinRuntime" in content, "Swift file missing KotlinRuntime import"
    assert "import KotlinRuntimeSupport" in content, "Swift file missing KotlinRuntimeSupport import"


def test_p2p_repo_structure_valid():
    """
    Pass-to-pass: Verify the repository structure is intact.
    """
    # Check that key directories exist
    dirs = [
        "native/swift/swift-export-standalone",
        "native/swift/swift-export-standalone-integration-tests",
        "native/swift/swift-export-standalone-integration-tests/coroutines",
    ]

    for d in dirs:
        path = os.path.join(REPO, d)
        assert os.path.isdir(path), f"Required directory missing: {d}"




def test_p2p_git_repo_clean():
    """
    Pass-to-pass: Git repository is accessible and functional (pass_to_pass).
    Runs actual git status command to verify git works.
    Note: After gold patch, working tree will have changes - we only verify git works.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    # Just verify git status executed successfully - git is functional
    # (we don't check if tree is clean because gold patch applies changes)


def test_p2p_java_version():
    """
    Pass-to-pass: Java version is correct (OpenJDK 21) (pass_to_pass).
    Runs actual java -version command.
    """
    r = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Java version check failed: {r.stderr}"
    # Check that output contains OpenJDK 21
    output = r.stderr + r.stdout
    assert "21." in output, f"Expected Java 21, got:\n{output}"


def test_p2p_shell_scripts_syntax_valid():
    """
    Pass-to-pass: Shell scripts have valid syntax (pass_to_pass).
    Runs bash -n to check syntax of key scripts.
    """
    scripts = [
        "scripts/build-kotlin-compiler.sh",
        "scripts/build-kotlin-maven.sh",
    ]

    for script in scripts:
        script_path = os.path.join(REPO, script)
        if os.path.exists(script_path):
            r = subprocess.run(
                ["bash", "-n", script_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert r.returncode == 0, f"Shell script {script} has syntax errors: {r.stderr}"

# ==============================================================================

def test_p2p_git_tracked_files():
    """
    Pass-to-pass: Core Swift export files are tracked by git (repo_tests).
    Runs git ls-files to verify files are tracked.
    """
    r = subprocess.run(
        ["git", "ls-files", "native/swift/swift-export-standalone/resources/swift/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git ls-files failed: {r.stderr}"
    output = r.stdout
    assert "KotlinCoroutineSupport.kt" in output, "KotlinCoroutineSupport.kt not tracked"
    assert "KotlinCoroutineSupport.swift" in output, "KotlinCoroutineSupport.swift not tracked"
    assert "KotlinCoroutineSupport.h" in output, "KotlinCoroutineSupport.h not tracked"


def test_p2p_shell_scripts_all_valid():
    """
    Pass-to-pass: All shell scripts in scripts/ have valid syntax (repo_tests).
    Runs bash -n on each script to check syntax.
    """
    scripts = [
        "scripts/build-kotlin-compiler.sh",
        "scripts/build-kotlin-maven.sh",
    ]
    for script in scripts:
        script_path = os.path.join(REPO, script)
        if os.path.exists(script_path):
            r = subprocess.run(
                ["bash", "-n", script_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert r.returncode == 0, f"Script {script} has syntax errors: {r.stderr}"


def test_p2p_git_log_works():
    """
    Pass-to-pass: Git log works and shows expected commit (repo_tests).
    Verifies git history is accessible.
    """
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    # Just verify we got some output
    assert len(r.stdout.strip()) > 0, "Git log returned empty output"


def test_p2p_gradle_help_works():
    """
    Pass-to-pass: Gradle wrapper is executable and can show help (repo_tests).
    Runs ./gradlew --help to verify gradle works.
    """
    r = subprocess.run(
        ["./gradlew", "--help"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Gradle might download, so check that it at least starts
    assert r.returncode == 0 or "gradle" in r.stdout.lower() or "gradle" in r.stderr.lower(), \
        f"Gradle help failed: {r.stderr[:500]}"


# FAIL_TO_PASS TESTS - The actual fix verification
# These tests verify the nullable Flow fix is properly implemented.
# They should FAIL on base commit and PASS after the fix.
# ==============================================================================


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
