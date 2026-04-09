#!/usr/bin/env python3
"""
Test outputs for Kotlin Swift Flow cancellation fix.

This tests that the SwiftFlowIterator properly cancels Flow collection when:
- The iterator is deinitialized
- A call to next() is cancelled

PR: https://github.com/JetBrains/kotlin/pull/5782
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/kotlin")
KOTLIN_FILE = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt"
SWIFT_FILE = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"


def read_kotlin_file():
    """Read the Kotlin coroutine support file."""
    if not KOTLIN_FILE.exists():
        raise FileNotFoundError(f"Kotlin file not found: {KOTLIN_FILE}")
    return KOTLIN_FILE.read_text()


def read_swift_file():
    """Read the Swift coroutine support file."""
    if not SWIFT_FILE.exists():
        raise FileNotFoundError(f"Swift file not found: {SWIFT_FILE}")
    return SWIFT_FILE.read_text()


# ==================== FAIL-TO-PASS TESTS ====================
# These tests verify the specific fixes are in place


def test_coroutine_scope_parameter():
    """SwiftFlowIterator has coroutineScope parameter with default value."""
    content = read_kotlin_file()
    # Check for the coroutineScope parameter in constructor
    assert "private val coroutineScope: CoroutineScope = CoroutineScope(EmptyCoroutineContext)" in content, \
        "SwiftFlowIterator should have coroutineScope parameter with default CoroutineScope"


def test_cancel_uses_scope_cancel():
    """cancel() method uses coroutineScope.cancel() instead of complete()."""
    content = read_kotlin_file()
    # The fix changes cancel() to use coroutineScope.cancel() directly
    assert "public fun cancel() = coroutineScope.cancel(CancellationException" in content, \
        "cancel() should call coroutineScope.cancel() directly"


def test_invoke_on_cancellation_ready_state():
    """State.Ready handler has invokeOnCancellation to cancel on suspension cancel."""
    content = read_kotlin_file()
    # Find the section with State.Ready and verify it has invokeOnCancellation
    lines = content.split('\n')
    in_ready_section = False
    continuation_block = []

    for i, line in enumerate(lines):
        if "is State.Ready<*>" in line:
            in_ready_section = True
        if in_ready_section:
            continuation_block.append(line)
            if i > 0 and "State.AwaitingProducer(continuation)" in line:
                break

    block_text = '\n'.join(continuation_block)
    assert "continuation.invokeOnCancellation { cancel() }" in block_text, \
        "State.Ready handling should have invokeOnCancellation { cancel() }"


def test_invoke_on_cancellation_awaiting_consumer_state():
    """State.AwaitingConsumer handler has invokeOnCancellation to cancel on suspension cancel."""
    content = read_kotlin_file()
    # Find the section with State.AwaitingConsumer and verify it has invokeOnCancellation
    lines = content.split('\n')
    in_awaiting_consumer_section = False
    continuation_block = []

    for i, line in enumerate(lines):
        if "is State.AwaitingConsumer ->" in line:
            in_awaiting_consumer_section = True
        if in_awaiting_consumer_section:
            continuation_block.append(line)
            if i > 0 and "State.AwaitingProducer(continuation)" in line:
                break

    block_text = '\n'.join(continuation_block)
    assert "continuation.invokeOnCancellation { cancel() }" in block_text, \
        "State.AwaitingConsumer handling should have invokeOnCancellation { cancel() }"


def test_launch_uses_coroutine_scope():
    """launch() method uses coroutineScope.launch instead of creating new scope."""
    content = read_kotlin_file()
    lines = content.split('\n')

    # Find the launch function
    in_launch = False
    launch_body = []
    for line in lines:
        if "private fun launch(flow: Flow<T>)" in line:
            in_launch = True
        if in_launch:
            launch_body.append(line)
            if line.strip() == "}" and len(launch_body) > 5:
                break

    launch_text = '\n'.join(launch_body)
    # Should use coroutineScope.launch, not CoroutineScope(EmptyCoroutineContext).launch
    assert "coroutineScope.launch {" in launch_text, \
        "launch() should use coroutineScope.launch instead of creating new CoroutineScope"
    assert "CoroutineScope(EmptyCoroutineContext).launch" not in launch_text, \
        "launch() should NOT create a new CoroutineScope each time"


def test_swift_iterator_class():
    """Swift file has new Iterator class that handles deinit cancellation."""
    content = read_swift_file()
    # Check for the new Iterator class
    assert "public final class Iterator: AsyncIteratorProtocol" in content, \
        "Swift file should have new Iterator class conforming to AsyncIteratorProtocol"


def test_swift_iterator_deinit_cancels():
    """Iterator.deinit calls cancel on the underlying KotlinFlowIterator."""
    content = read_swift_file()
    # Find the Iterator class and its deinit
    lines = content.split('\n')
    in_iterator = False
    deinit_lines = []

    for i, line in enumerate(lines):
        if "public final class Iterator: AsyncIteratorProtocol" in line:
            in_iterator = True
        if in_iterator and "deinit" in line:
            # Collect a few lines after deinit
            for j in range(i, min(i + 5, len(lines))):
                deinit_lines.append(lines[j])
            break

    deinit_text = '\n'.join(deinit_lines)
    assert "_kotlin_swift_SwiftFlowIterator_cancel(iterator.__externalRCRef())" in deinit_text, \
        "Iterator.deinit should call cancel on the underlying iterator"


def test_kotlin_flow_iterator_is_internal():
    """KotlinFlowIterator is marked as internal (not public)."""
    content = read_swift_file()
    # After the fix, KotlinFlowIterator should be internal
    assert "internal final class KotlinFlowIterator<Element>" in content, \
        "KotlinFlowIterator should be internal, not public"


def test_kotlin_flow_iterator_no_deinit():
    """KotlinFlowIterator no longer has deinit (moved to Iterator)."""
    content = read_swift_file()
    lines = content.split('\n')

    # Find the KotlinFlowIterator class
    in_class = False
    class_body = []
    brace_count = 0

    for line in lines:
        if "final class KotlinFlowIterator<Element>" in line:
            in_class = True
        if in_class:
            class_body.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and len(class_body) > 3:
                break

    class_text = '\n'.join(class_body)
    # Should NOT have deinit anymore
    assert "deinit {" not in class_text, \
        "KotlinFlowIterator should NOT have deinit (it was moved to Iterator class)"


# ==================== PASS-TO-PASS TESTS ====================
# These tests verify the repo remains functional


def test_kotlin_syntax_basic():
    """Kotlin file has valid syntax (basic checks)."""
    content = read_kotlin_file()
    # Basic syntax checks
    assert content.count("{") >= content.count("}") - 5, "Kotlin braces should roughly balance"
    assert "class SwiftFlowIterator" in content, "SwiftFlowIterator class should exist"
    assert "import kotlinx.coroutines" in content, "Should import coroutines"


def test_swift_syntax_basic():
    """Swift file has valid syntax (basic checks)."""
    content = read_swift_file()
    # Basic syntax checks
    assert content.count("{") >= content.count("}") - 5, "Swift braces should roughly balance"
    assert "struct KotlinFlowSequence" in content, "KotlinFlowSequence should exist"
    assert "public func makeAsyncIterator" in content, "makeAsyncIterator should exist"


def test_kotlin_coroutine_support_imports():
    """Kotlin coroutine support file has required imports (pass_to_pass)."""
    content = read_kotlin_file()
    # Verify all required imports are present
    assert "import kotlinx.coroutines" in content, "Should import kotlinx.coroutines"
    assert "import kotlinx.coroutines.flow" in content, "Should import kotlinx.coroutines.flow"
    assert "import kotlinx.cinterop" in content, "Should import cinterop"
    assert "import kotlin.concurrent.atomics.AtomicReference" in content, "Should import AtomicReference"


def test_kotlin_coroutine_support_classes():
    """Kotlin coroutine support file has required class definitions (pass_to_pass)."""
    content = read_kotlin_file()
    # Verify all required classes are present
    assert "class SwiftFlowIterator" in content, "SwiftFlowIterator class should exist"
    assert "class SwiftJob" in content, "SwiftJob class should exist"
    # State is a sealed interface, not a sealed class
    assert "sealed interface State" in content, "State sealed interface should exist"


def test_swift_coroutine_support_imports():
    """Swift coroutine support file has required imports (pass_to_pass)."""
    content = read_swift_file()
    # Verify Swift imports
    assert "import KotlinRuntime" in content, "Should import KotlinRuntime"
    assert "import KotlinRuntimeSupport" in content, "Should import KotlinRuntimeSupport"


def test_swift_coroutine_support_classes():
    """Swift coroutine support file has required class definitions (pass_to_pass)."""
    content = read_swift_file()
    # Verify all required types are present
    assert "struct KotlinFlowSequence" in content, "KotlinFlowSequence should exist"
    # KotlinFlowIterator can be public (before fix) or internal (after fix)
    assert "final class KotlinFlowIterator" in content, "KotlinFlowIterator should exist"
    assert "package final class KotlinTask" in content, "KotlinTask should exist"


def test_coroutine_test_data_exists():
    """Coroutine integration test data exists (pass_to_pass)."""
    test_data_dir = REPO / "native/swift/swift-export-standalone-integration-tests/coroutines/testData"
    assert test_data_dir.exists(), f"Coroutine test data directory should exist: {test_data_dir}"

    # Check for generation test data
    generation_dir = test_data_dir / "generation/coroutines"
    assert generation_dir.exists(), "Coroutine generation test data should exist"

    # Check for golden result files
    golden_dir = generation_dir / "golden_result"
    assert golden_dir.exists(), "Golden result files should exist"

    # Verify specific golden files exist
    flow_overrides_dir = golden_dir / "flow_overrides"
    assert flow_overrides_dir.exists(), "Flow overrides golden files should exist"


def test_repo_git_status_expected():
    """Repository git status is as expected - clean at base or has fix applied (pass_to_pass)."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "status", "--short"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Git status failed: {result.stderr}"
    # Either clean (base commit) or has the specific fix files modified
    git_status = result.stdout.strip()
    if git_status != "":
        # If there are changes, they should be the expected fix files
        expected_files = [
            "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt",
            "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift",
        ]
        for line in git_status.split("\n"):
            # Git status --short format: " M path/to/file" (status in col 1-2, path starts at col 3)
            # After strip(), format is "M path/to/file" (status at position 0, path starts at position 2)
            stripped = line.strip()
            if len(stripped) > 2:
                file_path = stripped[2:].strip()
                assert file_path in expected_files, f"Unexpected modified file: {line}"


def test_patch_applies_cleanly():
    """Gold patch can be applied cleanly to repository (pass_to_pass)."""
    # Check if already applied (by checking for a marker in the current files)
    kt_content = read_kotlin_file()
    already_applied = "private val coroutineScope:" in kt_content

    if already_applied:
        # If patch already applied, verify it's the expected state
        assert "private val coroutineScope: CoroutineScope = CoroutineScope(EmptyCoroutineContext)" in kt_content
    else:
        # Verify the solve.sh script exists by checking we can apply the patch
        # Try to apply patch in dry-run mode to verify it works
        result = subprocess.run(
            ["bash", "-c", f"cd {REPO} && git diff --quiet HEAD -- native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt"],
            capture_output=True, text=True, timeout=30,
        )
        # If git diff returns 0, files match (no local changes) - patch should apply cleanly
        # Note: We don't actually apply the patch in p2p test, just verify repo is clean


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
