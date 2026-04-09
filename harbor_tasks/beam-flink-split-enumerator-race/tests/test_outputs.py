"""
Task: beam-flink-split-enumerator-race
Repo: beam @ 28a0cb14ebd018e3550637ded153569d49e66f66
PR:   38083

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This is a Java file in the apache/beam monorepo. The class cannot
be compiled in isolation (deep Flink/Beam dependency graph), so tests use
source analysis + a standalone Java subprocess test for the concurrency pattern.
"""

import subprocess
import re
import os
from pathlib import Path

REPO = "/workspace/beam"
TARGET_FILE = os.path.join(
    REPO,
    "runners", "flink", "src", "main", "java", "org", "apache", "beam",
    "runners", "flink", "translation", "wrappers", "streaming", "io",
    "source", "LazyFlinkSourceSplitEnumerator.java",
)


def _read_source():
    return Path(TARGET_FILE).read_text()


def _extract_method(source, method_name):
    """Extract a Java method body by name using brace-counting."""
    pattern = re.compile(
        rf"(?:public|private|protected|\s)+[\w<>,\s\[\]?@]*\s+{method_name}\s*\([^)]*\)[^{{]*\{{",
        re.DOTALL,
    )
    match = pattern.search(source)
    if not match:
        return ""
    brace_count = 0
    for i in range(match.end() - 1, len(source)):
        if source[i] == "{":
            brace_count += 1
        elif source[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                return source[match.start() : i + 1]
    return source[match.start() :]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_java_syntax_valid():
    """Target Java file has valid structure (balanced braces, class declaration)."""
    src = _read_source()

    # Must have the class declaration
    assert re.search(
        r"class\s+LazyFlinkSourceSplitEnumerator", src
    ), "Class declaration not found"

    # Balanced braces
    assert src.count("{") == src.count(
        "}"
    ), f"Unbalanced braces: {src.count('{')} opens vs {src.count('}')} closes"

    # Must have both key methods
    assert "handleSplitRequest" in src, "handleSplitRequest method not found"
    assert "initializeSplits" in src, "initializeSplits method not found"


# [static] pass_to_pass
def test_java_imports_valid():
    """Target Java file has valid import statements (pass_to_pass)."""
    src = _read_source()

    # Extract all import statements
    import_pattern = re.compile(r"^import\s+([\w.]+);", re.MULTILINE)
    imports = import_pattern.findall(src)

    # Must have imports
    assert len(imports) > 0, "No import statements found"

    # All imports must be valid Java identifiers
    for imp in imports:
        parts = imp.split(".")
        for part in parts:
            assert re.match(r"^[a-zA-Z_]\w*$", part), f"Invalid identifier in import: {part}"

    # Must have key imports for Flink integration
    assert any("org.apache.flink" in imp for imp in imports), "Missing Flink imports"
    assert any("org.apache.beam" in imp for imp in imports), "Missing Beam imports"


# [static] pass_to_pass
def test_java_class_structure_valid():
    """Target Java file has valid class structure with proper nesting (pass_to_pass)."""
    src = _read_source()

    # Find class declaration with generics and implements
    class_match = re.search(
        r"public\s+class\s+LazyFlinkSourceSplitEnumerator<([^>]+)>\s+implements\s+([^\{]+)",
        src
    )
    assert class_match, "Class declaration with generics and implements not found"

    # Verify class body has balanced braces by parsing structure
    class_start = src.find("public class LazyFlinkSourceSplitEnumerator")
    assert class_start != -1, "Class start not found"

    brace_start = src.find("{", class_start)
    assert brace_start != -1, "Opening brace not found after class declaration"

    # Count braces to find class body end
    brace_count = 1
    pos = brace_start + 1
    while pos < len(src) and brace_count > 0:
        if src[pos] == "{":
            brace_count += 1
        elif src[pos] == "}":
            brace_count -= 1
        pos += 1

    assert brace_count == 0, "Class body has unbalanced braces"

    # Extract class body and check for required fields/methods
    class_body = src[brace_start:pos]

    # Must have private fields
    assert re.search(r"private\s+\w+", class_body), "No private fields found"

    # Must have constructor
    assert re.search(r"public\s+LazyFlinkSourceSplitEnumerator\s*\(", src), "Constructor not found"

    # Must have proper method signatures
    assert re.search(
        r"public\s+void\s+handleSplitRequest\s*\(", src
    ), "handleSplitRequest method declaration invalid"
    assert re.search(
        r"public\s+void\s+initializeSplits\s*\(", src
    ), "initializeSplits method declaration invalid"




# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_handle_split_request_blocks_on_uninitialized():
    """handleSplitRequest must block/wait until splits initialization completes.

    The bug: handleSplitRequest could be called before the async initializeSplits
    finished, seeing pendingSplits as empty and incorrectly signaling no more splits.
    The fix must add a blocking wait mechanism.
    """
    src = _read_source()
    method = _extract_method(src, "handleSplitRequest")
    assert method, "handleSplitRequest method not found"

    # Must contain a blocking mechanism before accessing pendingSplits
    blocking_patterns = [
        r"\.await\s*\(",  # CountDownLatch.await()
        r"\.wait\s*\(",  # Object.wait()
        r"\.get\s*\(",  # Future.get()
        r"\.join\s*\(",  # CompletableFuture.join()
        r"\.acquire\s*\(",  # Semaphore.acquire()
        r"synchronized\s*\(",  # synchronized block
    ]
    has_blocking = any(re.search(p, method) for p in blocking_patterns)
    assert has_blocking, (
        "handleSplitRequest must block until initialization completes "
        "(e.g., CountDownLatch.await, Future.get, synchronized+wait)"
    )


# [pr_diff] fail_to_pass
def test_splits_initialized_thread_safe():
    """splitsInitialized field must be thread-safe for cross-thread visibility.

    Without volatile or equivalent, the JMM allows one thread to write true
    while another thread reads a stale false value.
    """
    src = _read_source()

    # Option 1: volatile boolean
    has_volatile = bool(
        re.search(r"volatile\s+boolean\s+splitsInitialized", src)
    )
    # Option 2: AtomicBoolean
    has_atomic = "AtomicBoolean" in src and "splitsInitialized" in src
    # Option 3: all accesses in synchronized blocks
    has_sync = "synchronized" in src and "splitsInitialized" in src

    assert has_volatile or has_atomic or has_sync, (
        "splitsInitialized must be thread-safe: use volatile, AtomicBoolean, "
        "or synchronized access"
    )


# [pr_diff] fail_to_pass
def test_initialization_signals_in_finally():
    """initializeSplits must signal completion in a finally block.

    The async callable in initializeSplits can throw. If the signal is only
    in the happy path, a failure would leave handleSplitRequest blocked forever.
    A finally block ensures the signal fires regardless of outcome.
    """
    src = _read_source()
    method = _extract_method(src, "initializeSplits")
    assert method, "initializeSplits method not found"

    # Must have a finally block
    assert "finally" in method, (
        "initializeSplits must use a finally block to ensure completion is "
        "signaled even when initialization fails"
    )

    # The finally block must contain a signal mechanism
    finally_match = re.search(r"finally\s*\{([^}]*)\}", method)
    assert finally_match, "finally block not found in initializeSplits"
    finally_body = finally_match.group(1)

    signal_patterns = [
        r"\.countDown\s*\(",  # CountDownLatch
        r"\.release\s*\(",  # Semaphore
        r"\.notify",  # Object.notify/notifyAll
        r"\.complete\s*\(",  # CompletableFuture
        r"\.set\s*\(",  # AtomicBoolean
        r"\.signal\s*\(",  # Condition
    ]
    has_signal = any(re.search(p, finally_body) for p in signal_patterns)
    assert has_signal, (
        "finally block in initializeSplits must signal completion "
        "(countDown, release, notify, complete, etc.)"
    )


# [pr_diff] fail_to_pass
def test_synchronization_fix_java_validation():
    """Compile and run a standalone Java program that validates the sync pattern.

    This uses subprocess to compile/run Java code that reads the source and
    validates the concurrency fix is structurally correct.
    """
    java_code = r'''
import java.nio.file.*;
import java.util.regex.*;

public class ValidateSyncFix {
    public static void main(String[] args) throws Exception {
        String src = Files.readString(Path.of(args[0]));

        // 1. Must import a java.util.concurrent synchronization primitive
        boolean hasConcurrentImport =
            src.contains("import java.util.concurrent.CountDownLatch") ||
            src.contains("import java.util.concurrent.Semaphore") ||
            src.contains("import java.util.concurrent.CompletableFuture") ||
            src.contains("import java.util.concurrent.locks.");
        if (!hasConcurrentImport) {
            fail("Must import a java.util.concurrent synchronization primitive");
        }

        // 2. splitsInitialized must be volatile or AtomicBoolean
        if (!Pattern.compile("volatile\\s+boolean\\s+splitsInitialized").matcher(src).find() &&
            !src.contains("AtomicBoolean")) {
            fail("splitsInitialized must be volatile or AtomicBoolean");
        }

        // 3. handleSplitRequest must contain a blocking call
        String handleMethod = extractMethod(src, "handleSplitRequest");
        if (handleMethod.isEmpty()) {
            fail("handleSplitRequest method not found");
        }
        boolean hasBlocking =
            handleMethod.contains(".await(") ||
            handleMethod.contains(".get(") ||
            handleMethod.contains(".join(") ||
            handleMethod.contains(".acquire(") ||
            (handleMethod.contains("synchronized") && handleMethod.contains(".wait("));
        if (!hasBlocking) {
            fail("handleSplitRequest must block until initialization completes");
        }

        // 4. handleSplitRequest must handle InterruptedException
        if (!handleMethod.contains("InterruptedException")) {
            fail("handleSplitRequest must handle InterruptedException from blocking wait");
        }

        System.out.println("All synchronization validations passed");
    }

    static String extractMethod(String src, String name) {
        int idx = src.indexOf("void " + name + "(");
        if (idx < 0) idx = src.indexOf(name + "(");
        if (idx < 0) return "";
        int brace = src.indexOf('{', idx);
        if (brace < 0) return "";
        int count = 1, end = brace + 1;
        while (end < src.length() && count > 0) {
            if (src.charAt(end) == '{') count++;
            else if (src.charAt(end) == '}') count--;
            end++;
        }
        return src.substring(idx, end);
    }

    static void fail(String msg) {
        System.err.println("FAIL: " + msg);
        System.exit(1);
    }
}
'''

    test_dir = Path("/tmp/validate_sync_fix")
    test_dir.mkdir(exist_ok=True)
    (test_dir / "ValidateSyncFix.java").write_text(java_code)

    # Compile the Java validator
    r = subprocess.run(
        ["javac", "ValidateSyncFix.java"],
        cwd=str(test_dir),
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, f"Java validator compilation failed: {r.stderr.decode()}"

    # Run against the target file
    r = subprocess.run(
        ["java", "-cp", str(test_dir), "ValidateSyncFix", TARGET_FILE],
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, f"Sync fix validation failed: {r.stderr.decode()}"


# [static] pass_to_pass
def test_java_no_syntax_errors():
    """Target Java file has no obvious syntax errors (pass_to_pass)."""
    src = _read_source()

    # Check for valid Java identifiers in field declarations
    field_pattern = re.compile(r"(?:private|public|protected)\s+(?:\w+\s+)*(\w+)\s+\w+\s*[=;]")
    for match in field_pattern.finditer(src):
        type_name = match.group(1)
        # Type name should be a valid Java identifier
        assert re.match(r"^[a-zA-Z_]\w*$", type_name), f"Invalid type name: {type_name}"

    # Verify no empty catch blocks (common issue)
    assert not re.search(r"catch\s*\([^)]+\)\s*\{\s*\}", src), "Empty catch block found"

    # Check for balanced braces at file level
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} opens vs {close_braces} closes"

    # Check for obvious syntax errors like double semicolons
    assert ";;" not in src, "Double semicolon found"

    # Check for valid package declaration
    assert re.search(r"^package\s+[\w.]+;", src, re.MULTILINE), "Package declaration not found or invalid"
