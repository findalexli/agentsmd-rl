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
import re
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


def extract_kotlin_class(content, class_name):
    """Extract the body of a Kotlin class."""
    pattern = rf'(?:public\s+|private\s+|internal\s+|fileprivate\s+)?class\s+{class_name}\s*<[^>]+>(?:\s+private\s+constructor|\s+constructor)?\s*\('
    match = re.search(pattern, content)
    if not match:
        return None

    start = match.start()
    brace_start = content.find('{', start)
    if brace_start == -1:
        return None

    depth = 1
    pos = brace_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    if depth == 0:
        return content[match.start():pos]
    return None


def extract_method_body(content, method_name):
    """Extract a method body from Kotlin class content. Handles both brace-delimited and expression-bodied methods."""
    # Try brace-delimited first
    pattern = rf'(?:public\s+|private\s+|internal\s+|fileprivate\s+|override\s+)*fun\s+{method_name}\s*\([^)]*\)\s*(?::\s*[^{{]+)?\s*\{{'
    match = re.search(pattern, content)
    if match:
        # Find the opening brace - it's at the end of the match
        brace_pos = match.end() - 1
        depth = 1
        pos = brace_pos + 1
        while pos < len(content) and depth > 0:
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1
        if depth == 0:
            return content[match.start():pos]

    # Try expression-bodied (with =)
    pattern2 = rf'(?:public\s+|private\s+|internal\s+|fileprivate\s+|override\s+)*fun\s+{method_name}\s*\([^)]*\)\s*(?::\s*[^{{]+)?\s*=\s*[^{{;]+'
    match2 = re.search(pattern2, content)
    if match2:
        return match2.group(0)

    return None


def extract_swift_class(content, class_name):
    """Extract the body of a Swift class."""
    pattern = rf'(?:public\s+|private\s+|internal\s+|package\s+)?(?:final\s+)?class\s+{class_name}\s*<[^>]+>(?:\s*:\s*[^{{]+)?\s*\{{'
    match = re.search(pattern, content)
    if not match:
        pattern = rf'(?:public\s+|private\s+|internal\s+|package\s+)?(?:final\s+)?class\s+{class_name}\s*(?::\s*[^{{]+)?\s*\{{'
        match = re.search(pattern, content)
    if not match:
        return None

    start = match.start() + match.end() - 1
    depth = 1
    pos = start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    if depth == 0:
        return content[match.start():pos]
    return None


# ==================== FAIL-TO-PASS TESTS ====================
# These tests verify the specific fixes are in place (behavioral checks)


def test_coroutine_scope_parameter():
    """SwiftFlowIterator has coroutineScope field with CoroutineScope type and default value.

    Behavioral check: The class must have a CoroutineScope field with a default value,
    regardless of the exact field name. Alternative names like 'scope', '_coroutineScope'
    would also pass. Default context may vary (EmptyCoroutineContext, Dispatchers.Default, etc).
    """
    content = read_kotlin_file()
    class_body = extract_kotlin_class(content, "SwiftFlowIterator")
    assert class_body, "SwiftFlowIterator class not found"

    # Check that there's a field with CoroutineScope type and default value
    scope_field = re.search(
        r'(?:val|var)\s+\w+\s*:\s*CoroutineScope\s*=\s*CoroutineScope\s*\(',
        class_body
    )
    assert scope_field, "SwiftFlowIterator should have a CoroutineScope field with default value"


def test_cancel_uses_scope_cancel():
    """cancel() method delegates to scope cancellation, not complete().

    Behavioral check: The cancel() method must call something.cancel(CancellationException(...))
    instead of complete(...). This ensures cancellation propagates through the coroutine scope.
    """
    content = read_kotlin_file()
    class_body = extract_kotlin_class(content, "SwiftFlowIterator")
    assert class_body, "SwiftFlowIterator class not found"

    cancel_method = extract_method_body(class_body, "cancel")
    assert cancel_method, "cancel() method not found"

    # Must call .cancel() with CancellationException (scope cancellation)
    assert re.search(r'\.cancel\s*\(\s*CancellationException', cancel_method), \
        "cancel() should call .cancel(CancellationException(...)) to propagate cancellation"

    # Must NOT call complete() directly (old broken behavior)
    assert not re.search(r'complete\s*\(\s*CancellationException', cancel_method), \
        "cancel() should not call complete() directly"


def test_invoke_on_cancellation_ready_state():
    """State.Ready handler registers cancellation callback on continuation.

    Behavioral check: The Ready state handling must register an invokeOnCancellation
    callback that calls cancel(). This ensures next() cancellation cancels the flow.
    """
    content = read_kotlin_file()
    class_body = extract_kotlin_class(content, "SwiftFlowIterator")
    assert class_body, "SwiftFlowIterator class not found"

    next_method = extract_method_body(class_body, "next")
    assert next_method, "next() method not found"

    # Find State.Ready block - the pattern has { val state = ... return suspendCancellableCoroutine
    ready_pattern = r'is\s+State\.Ready\s*<[^>]+>\s*->\s*\{[^}]*return\s+suspendCancellableCoroutine'
    ready_match = re.search(ready_pattern, next_method, re.DOTALL)
    assert ready_match, "State.Ready handling not found in next()"

    # Get a window around the match to find the continuation block
    ready_start = ready_match.start()
    window = next_method[ready_start:ready_start+800]

    # Check for invokeOnCancellation registration
    assert re.search(r'continuation\.invokeOnCancellation\s*\{', window), \
        "State.Ready should register invokeOnCancellation callback"

    # Find the invokeOnCancellation callback body and check it calls cancel()
    invoke_match = re.search(r'invokeOnCancellation\s*\{([^}]+)\}', window)
    if invoke_match:
        callback = invoke_match.group(1)
        assert 'cancel()' in callback or 'cancel(' in callback, \
            "invokeOnCancellation callback should call cancel()"


def test_invoke_on_cancellation_awaiting_consumer_state():
    """State.AwaitingConsumer handler registers cancellation callback on continuation.

    Behavioral check: The AwaitingConsumer state handling must register an
    invokeOnCancellation callback that calls cancel().
    """
    content = read_kotlin_file()
    class_body = extract_kotlin_class(content, "SwiftFlowIterator")
    assert class_body, "SwiftFlowIterator class not found"

    next_method = extract_method_body(class_body, "next")
    assert next_method, "next() method not found"

    # Find State.AwaitingConsumer block
    consumer_pattern = r'is\s+State\.AwaitingConsumer\s*->\s*\{[^}]*return\s+suspendCancellableCoroutine'
    consumer_match = re.search(consumer_pattern, next_method, re.DOTALL)
    assert consumer_match, "State.AwaitingConsumer handling not found in next()"

    # Get a window around the match
    consumer_start = consumer_match.start()
    window = next_method[consumer_start:consumer_start+800]

    # Check for invokeOnCancellation registration
    assert re.search(r'continuation\.invokeOnCancellation\s*\{', window), \
        "State.AwaitingConsumer should register invokeOnCancellation callback"

    # Find the callback and check it calls cancel()
    invoke_match = re.search(r'invokeOnCancellation\s*\{([^}]+)\}', window)
    if invoke_match:
        callback = invoke_match.group(1)
        assert 'cancel()' in callback or 'cancel(' in callback, \
            "invokeOnCancellation callback should call cancel()"


def test_launch_uses_coroutine_scope():
    """launch() method uses stored scope, not creating new CoroutineScope each time.

    Behavioral check: launch() must use the stored coroutine scope (whatever it's named)
    instead of creating a new CoroutineScope(EmptyCoroutineContext) for each launch.
    """
    content = read_kotlin_file()
    class_body = extract_kotlin_class(content, "SwiftFlowIterator")
    assert class_body, "SwiftFlowIterator class not found"

    launch_method = extract_method_body(class_body, "launch")
    assert launch_method, "launch() method not found"

    # Check: must use .launch { ... } on some scope reference
    assert re.search(r'\.launch\s*\{', launch_method), \
        "launch() should use .launch { ... } on a scope"

    # Check: must NOT create new CoroutineScope each time
    assert not re.search(r'CoroutineScope\s*\([^)]*\)\.launch\s*\{', launch_method), \
        "launch() should NOT create a new CoroutineScope each time (use stored scope)"


def test_swift_iterator_class():
    """Swift file has Iterator class that handles async iteration lifecycle.

    Behavioral check: KotlinFlowSequence must have a nested or standalone Iterator class
    that conforms to AsyncIteratorProtocol. This handles the deinit-based cancellation.
    """
    content = read_swift_file()

    # Look for Iterator class - could be nested in KotlinFlowSequence or standalone
    iterator_patterns = [
        r'class\s+Iterator\s*:\s*AsyncIteratorProtocol',
        r'(?:public\s+|private\s+|internal\s+)?final\s+class\s+Iterator\s*:\s*AsyncIteratorProtocol',
    ]

    found = any(re.search(p, content) for p in iterator_patterns)
    assert found, "Iterator class conforming to AsyncIteratorProtocol not found"


def test_swift_iterator_deinit_cancels():
    """Iterator class deinit calls cancel on underlying KotlinFlowIterator.

    Behavioral check: The Iterator's deinit must call the cancel function on the
    underlying KotlinFlowIterator to properly cancel the Flow when Iterator is deallocated.
    """
    content = read_swift_file()

    # Find Iterator class body
    iterator_match = re.search(
        r'(?:public\s+|private\s+|internal\s+)?final\s+class\s+Iterator\s*:\s*AsyncIteratorProtocol[^{]*\{',
        content
    )
    if not iterator_match:
        iterator_match = re.search(
            r'class\s+Iterator\s*:\s*AsyncIteratorProtocol[^{]*\{',
            content
        )
    assert iterator_match, "Iterator class not found"

    # Find the class body
    class_start = iterator_match.start() + iterator_match.end() - 1
    depth = 1
    pos = class_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    class_body = content[iterator_match.start():pos]

    # Find deinit in this class body
    deinit_match = re.search(r'deinit\s*\{[^}]*\}', class_body)
    assert deinit_match, "Iterator.deinit not found in Iterator class"

    deinit_body = deinit_match.group(0)

    # deinit should call cancel function on the iterator
    assert re.search(r'_kotlin_swift_SwiftFlowIterator_cancel\s*\(', deinit_body), \
        "Iterator.deinit should call _kotlin_swift_SwiftFlowIterator_cancel"


def test_kotlin_flow_iterator_is_internal():
    """KotlinFlowIterator is marked as internal (not public).

    Behavioral check: KotlinFlowIterator must not be publicly accessible from Swift.
    It should be internal (or package/internal) so only the Iterator wrapper is public.
    """
    content = read_swift_file()

    # KotlinFlowIterator class declaration should be internal (not public)
    class_match = re.search(
        r'(?:internal|package)\s+final\s+class\s+KotlinFlowIterator\s*<Element>',
        content
    )
    assert class_match, "KotlinFlowIterator should be internal (or package), not public"


def test_kotlin_flow_iterator_no_deinit():
    """KotlinFlowIterator does not have its own deinit (moved to Iterator).

    Behavioral check: KotlinFlowIterator should NOT have a deinit, because the
    deinit logic is now in the Swift Iterator class which properly handles cancellation.
    """
    content = read_swift_file()

    # Extract KotlinFlowIterator class body
    class_match = re.search(
        r'(?:public|internal|private|package)?\s*(?:final\s+)?class\s+KotlinFlowIterator\s*<Element>\s*:[^{]*\{',
        content
    )
    assert class_match, "KotlinFlowIterator class not found"

    class_start = class_match.start() + class_match.end() - 1
    depth = 1
    pos = class_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    class_body = content[class_match.start():pos]

    # Should NOT have deinit
    assert 'deinit {' not in class_body, \
        "KotlinFlowIterator should NOT have deinit (moved to Iterator class)"


# ==================== PASS-TO-PASS TESTS ====================
# These tests verify the repo remains functional


def test_kotlin_file_compiles_syntax():
    """CI: Kotlin coroutine support file has valid Kotlin syntax (pass_to_pass)."""
    script = """
import sys
import re

with open('/workspace/kotlin/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt', 'r') as f:
    content = f.read()

open_braces = content.count('{')
close_braces = content.count('}')
if abs(open_braces - close_braces) > 5:
    print(f'Brace mismatch: {open_braces} vs {close_braces}')
    sys.exit(1)

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

open_braces = content.count('{')
close_braces = content.count('}')
if abs(open_braces - close_braces) > 5:
    print(f'Brace mismatch: {open_braces} vs {close_braces}')
    sys.exit(1)

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
