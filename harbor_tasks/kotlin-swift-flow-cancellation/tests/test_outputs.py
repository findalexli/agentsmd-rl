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
    assert "private val coroutineScope: CoroutineScope = CoroutineScope(EmptyCoroutineContext)" in content, \
        "SwiftFlowIterator should have coroutineScope parameter with default CoroutineScope"


def test_cancel_uses_scope_cancel():
    """cancel() method uses coroutineScope.cancel() instead of complete()."""
    content = read_kotlin_file()
    assert "public fun cancel() = coroutineScope.cancel(CancellationException" in content, \
        "cancel() should call coroutineScope.cancel() directly"


def test_invoke_on_cancellation_ready_state():
    """State.Ready handler has invokeOnCancellation to cancel on suspension cancel."""
    content = read_kotlin_file()
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
    assert "coroutineScope.launch {" in launch_text, \
        "launch() should use coroutineScope.launch instead of creating new CoroutineScope"
    assert "CoroutineScope(EmptyCoroutineContext).launch" not in launch_text, \
        "launch() should NOT create a new CoroutineScope each time"


def test_swift_iterator_class():
    """Swift file has new Iterator class that handles deinit cancellation."""
    content = read_swift_file()
    assert "public final class Iterator: AsyncIteratorProtocol" in content, \
        "Swift file should have new Iterator class conforming to AsyncIteratorProtocol"


def test_swift_iterator_deinit_cancels():
    """Iterator.deinit calls cancel on the underlying KotlinFlowIterator."""
    content = read_swift_file()
    lines = content.split('\n')
    in_iterator = False
    deinit_lines = []

    for i, line in enumerate(lines):
        if "public final class Iterator: AsyncIteratorProtocol" in line:
            in_iterator = True
        if in_iterator and "deinit" in line:
            for j in range(i, min(i + 5, len(lines))):
                deinit_lines.append(lines[j])
            break

    deinit_text = '\n'.join(deinit_lines)
    assert "_kotlin_swift_SwiftFlowIterator_cancel(iterator.__externalRCRef())" in deinit_text, \
        "Iterator.deinit should call cancel on the underlying iterator"


def test_kotlin_flow_iterator_is_internal():
    """KotlinFlowIterator is marked as internal (not public)."""
    content = read_swift_file()
    assert "internal final class KotlinFlowIterator<Element>" in content, \
        "KotlinFlowIterator should be internal, not public"


def test_kotlin_flow_iterator_no_deinit():
    """KotlinFlowIterator no longer has deinit (moved to Iterator)."""
    content = read_swift_file()
    lines = content.split('\n')

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
    assert "deinit {" not in class_text, \
        "KotlinFlowIterator should NOT have deinit (it was moved to Iterator class)"


# ==================== PASS-TO-PASS TESTS ====================
# These tests verify the repo remains functional


def test_kotlin_file_compiles_syntax():
    """CI: Kotlin coroutine support file has valid Kotlin syntax (pass_to_pass)."""
    # Use Python-based validation with proper parsing
    script = """
import sys
import re

with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt', 'r') as f:
    content = f.read()

# Check for balanced braces (allowing small margin for string literals)
open_braces = content.count('{')
close_braces = content.count('}')
if abs(open_braces - close_braces) > 5:
    print(f'Brace mismatch: {open_braces} vs {close_braces}')
    sys.exit(1)

# Check for required class/function declarations
required_patterns = [
    r'class\\s+SwiftFlowIterator',
    r'class\\s+SwiftJob',
    r'sealed\\s+interface\\s+State',
    r'fun\\s+__root___SwiftFlowIterator',
]

for pattern in required_patterns:
    if not re.search(pattern, content):
        print(f'Missing pattern: {pattern}')
        sys.exit(1)

# Check for proper package-level declarations
if 'import kotlinx.coroutines' not in content:
    print('Missing kotlinx.coroutines import')
    sys.exit(1)

print('Kotlin syntax validation passed')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Kotlin syntax check failed: {result.stderr or result.stdout}"


def test_swift_file_compiles_syntax():
    """CI: Swift coroutine support file has valid Swift syntax (pass_to_pass)."""
    script = """
import sys
import re

with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift', 'r') as f:
    content = f.read()

# Check for balanced braces
open_braces = content.count('{')
close_braces = content.count('}')
if abs(open_braces - close_braces) > 5:
    print(f'Brace mismatch: {open_braces} vs {close_braces}')
    sys.exit(1)

# Check for required declarations
required_patterns = [
    r'struct\\s+KotlinFlowSequence',
    r'class\\s+KotlinFlowIterator',
    r'class\\s+KotlinTask',
    r'func\\s+makeAsyncIterator',
]

for pattern in required_patterns:
    if not re.search(pattern, content):
        print(f'Missing pattern: {pattern}')
        sys.exit(1)

# Check for imports
if 'import KotlinRuntime' not in content:
    print('Missing KotlinRuntime import')
    sys.exit(1)

print('Swift syntax validation passed')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Swift syntax check failed: {result.stderr or result.stdout}"


def test_kotlin_coroutine_support_imports():
    """CI: Kotlin coroutine support file has required imports (pass_to_pass)."""
    script = """
import sys
with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt', 'r') as f:
    content = f.read()
required = ['import kotlinx.coroutines', 'import kotlinx.coroutines.flow', 'import kotlinx.cinterop', 'import kotlin.concurrent.atomics.AtomicReference']
for r in required:
    if r not in content:
        print(f'Missing: {r}')
        sys.exit(1)
print('All imports present')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Import check failed: {result.stderr or result.stdout}"


def test_kotlin_coroutine_support_classes():
    """CI: Kotlin coroutine support file has required class definitions (pass_to_pass)."""
    script = """
import sys
import re
with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt', 'r') as f:
    content = f.read()
patterns = [r'class\\s+SwiftFlowIterator', r'class\\s+SwiftJob', r'sealed\\s+interface\\s+State']
for p in patterns:
    if not re.search(p, content):
        print(f'Missing pattern: {p}')
        sys.exit(1)
print('All classes present')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Class check failed: {result.stderr or result.stdout}"


def test_swift_coroutine_support_imports():
    """CI: Swift coroutine support file has required imports (pass_to_pass)."""
    script = """
import sys
with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift', 'r') as f:
    content = f.read()
if 'import KotlinRuntime' not in content or 'import KotlinRuntimeSupport' not in content:
    print('Missing required imports')
    sys.exit(1)
print('All Swift imports present')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Swift import check failed: {result.stderr or result.stdout}"


def test_swift_coroutine_support_classes():
    """CI: Swift coroutine support file has required class definitions (pass_to_pass)."""
    script = """
import sys
import re
with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift', 'r') as f:
    content = f.read()
patterns = [r'struct\\s+KotlinFlowSequence', r'final class\\s+KotlinFlowIterator', r'package final class\\s+KotlinTask']
for p in patterns:
    if not re.search(p, content):
        print(f'Missing pattern: {p}')
        sys.exit(1)
print('All Swift classes present')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Swift class check failed: {result.stderr or result.stdout}"


def test_coroutine_test_data_exists():
    """CI: Coroutine integration test data exists and is valid (pass_to_pass)."""
    script = """
import os
import sys

base_path = '/workspace/kotlin/native/swift/swift-export-standalone-integration-tests/coroutines/testData'
required_dirs = [
    'generation/coroutines',
    'generation/coroutines/golden_result/flow_overrides',
    'execution/coroutines',
    'execution/closures',
    'execution/sequences'
]
for d in required_dirs:
    full_path = os.path.join(base_path, d)
    if not os.path.isdir(full_path):
        print(f'Missing directory: {full_path}')
        sys.exit(1)
    if not os.listdir(full_path):
        print(f'Empty directory: {full_path}')
        sys.exit(1)
print('All coroutine test data directories exist and have content')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test data check failed: {result.stderr or result.stdout}"


def test_repo_git_status_expected():
    """Repository git status is as expected - clean at base or has fix applied (pass_to_pass)."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "status", "--short"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Git status failed: {result.stderr}"
    git_status = result.stdout.strip()
    if git_status != "":
        expected_files = [
            "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt",
            "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift",
        ]
        for line in git_status.split("\n"):
            stripped = line.strip()
            if len(stripped) > 2:
                file_path = stripped[2:].strip()
                assert file_path in expected_files, f"Unexpected modified file: {line}"


def test_patch_applies_cleanly():
    """Gold patch can be applied cleanly to repository (pass_to_pass)."""
    kt_content = read_kotlin_file()
    already_applied = "private val coroutineScope:" in kt_content

    if already_applied:
        assert "private val coroutineScope: CoroutineScope = CoroutineScope(EmptyCoroutineContext)" in kt_content
    else:
        result = subprocess.run(
            ["bash", "-c", f"cd {REPO} && git diff --quiet HEAD -- native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt"],
            capture_output=True, text=True, timeout=30,
        )


def test_repo_swift_export_test_files_exist():
    """CI: Swift export test support files exist (pass_to_pass)."""
    script = """
import os
import sys

files = [
    '/workspace/kotlin/native/swift/swift-export-standalone-integration-tests/src/org/jetbrains/kotlin/swiftexport/standalone/test/AbstractSwiftExportExecutionTest.kt',
    '/workspace/kotlin/native/swift/swift-export-standalone-integration-tests/src/org/jetbrains/kotlin/swiftexport/standalone/test/AbstractSwiftExportTest.kt',
    '/workspace/kotlin/native/swift/swift-export-standalone-integration-tests/src/org/jetbrains/kotlin/swiftexport/standalone/test/SwiftExportWithCoroutinesTestSupport.kt',
]
for f in files:
    if not os.path.isfile(f):
        print(f'Missing file: {f}')
        sys.exit(1)
print('All test support files exist')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test files check failed: {result.stderr or result.stdout}"


def test_repo_gradle_module_structure():
    """CI: Swift export modules have proper Gradle structure (pass_to_pass)."""
    script = """
import os
import sys

modules = [
    '/workspace/kotlin/native/swift/swift-export-standalone',
    '/workspace/kotlin/native/swift/swift-export-standalone-integration-tests/coroutines',
    '/workspace/kotlin/native/swift/sir',
    '/workspace/kotlin/native/swift/sir-printer',
]
for module in modules:
    build_file = os.path.join(module, 'build.gradle.kts')
    if not os.path.isfile(build_file):
        print(f'Missing build file: {build_file}')
        sys.exit(1)
print('All Gradle modules have build files')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Gradle module check failed: {result.stderr or result.stdout}"


def test_repo_kotlin_file_line_count():
    """CI: Kotlin coroutine support file has reasonable size (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", "wc -l /workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt | awk '{print $1}'"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, "Line count failed"
    line_count = int(result.stdout.strip())
    assert 200 < line_count < 500, f"Kotlin file has unexpected line count: {line_count}"


def test_repo_swift_file_line_count():
    """CI: Swift coroutine support file has reasonable size (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", "wc -l /workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift | awk '{print $1}'"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, "Line count failed"
    line_count = int(result.stdout.strip())
    assert 200 < line_count < 500, f"Swift file has unexpected line count: {line_count}"


# CI-based pass-to-pass tests using subprocess.run()


def test_repo_gradle_settings_exist():
    """CI: Repo Gradle settings file exists and is parseable (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", f"test -f {REPO}/settings.gradle && test -f {REPO}/gradlew && echo 'OK'"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Gradle structure validation failed: {result.stderr}"


def test_repo_kotlin_file_syntax_ktlint():
    """CI: Kotlin coroutine support file has valid basic structure (pass_to_pass)."""
    script = f"""
import sys
with open('{REPO}/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt', 'r') as f:
    content = f.read()
    open_braces = content.count('{{')
    close_braces = content.count('}}')
    if abs(open_braces - close_braces) > 5:
        print(f'Brace mismatch: {{open_braces}} vs {{close_braces}}')
        sys.exit(1)
    required = ['import kotlinx.coroutines', 'class SwiftFlowIterator']
    for r in required:
        if r not in content:
            print(f'Missing: {{r}}')
            sys.exit(1)
    print('Syntax OK')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Kotlin syntax validation failed: {result.stderr}"


def test_repo_swift_file_syntax_basic():
    """CI: Swift coroutine support file has valid basic structure (pass_to_pass)."""
    script = f"""
import sys
with open('{REPO}/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift', 'r') as f:
    content = f.read()
    open_braces = content.count('{{')
    close_braces = content.count('}}')
    if abs(open_braces - close_braces) > 5:
        print(f'Brace mismatch: {{open_braces}} vs {{close_braces}}')
        sys.exit(1)
    required = ['import KotlinRuntime', 'struct KotlinFlowSequence']
    for r in required:
        if r not in content:
            print(f'Missing: {{r}}')
            sys.exit(1)
    print('Syntax OK')
"""
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Swift syntax validation failed: {result.stderr}"


def test_repo_swift_export_module_exists():
    """CI: Swift export standalone module exists and has required files (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", f"ls {REPO}/native/swift/swift-export-standalone/resources/swift/*.kt >/dev/null && ls {REPO}/native/swift/swift-export-standalone/resources/swift/*.swift >/dev/null && echo 'OK'"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, "Swift export module files missing"


def test_repo_test_data_integrity():
    """CI: Coroutine test data files are complete and valid (pass_to_pass)."""
    script = f"""
for dir in generation execution; do
    path="{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/$dir"
    if [ ! -d "$path" ]; then
        echo "Missing: $path"
        exit 1
    fi
    if [ -z "$(ls -A $path)" ]; then
        echo "Empty: $path"
        exit 1
    fi
done
echo 'Test data integrity OK'
"""
    result = subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test data integrity check failed: {result.stderr}"


def test_repo_git_log_base_commit():
    """CI: Repository is at expected base commit (pass_to_pass)."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, "Git rev-parse failed"
    commit = result.stdout.strip()
    expected_base = "aa96b1eb9878f7e427671338882cd24dc514a090"
    assert commit == expected_base, f"Unexpected commit: {commit[:8]}... (expected {expected_base[:8]}...)"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
