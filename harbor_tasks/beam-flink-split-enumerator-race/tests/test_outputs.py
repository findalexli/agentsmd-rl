"""
Task: beam-flink-split-enumerator-race
Repo: beam @ 28a0cb14ebd018e3550637ded153569d49e66f66
PR:   38083

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral approach: f2p tests verify the concurrency behavior by checking for
proper synchronization patterns. Tests accept ANY correct implementation using
java.util.concurrent primitives (CountDownLatch, Semaphore, Condition, etc.).
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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_java_syntax_valid():
    """Target Java file has valid structure (balanced braces, class declaration)."""
    src = _read_source()
    assert re.search(r"class\s+LazyFlinkSourceSplitEnumerator", src), "Class declaration not found"
    assert src.count("{") == src.count("}"), f"Unbalanced braces: {src.count('{')} opens vs {src.count('}')} closes"
    assert "handleSplitRequest" in src, "handleSplitRequest method not found"
    assert "initializeSplits" in src, "initializeSplits method not found"


# [static] pass_to_pass
def test_java_imports_valid():
    """Target Java file has valid import statements (pass_to_pass)."""
    src = _read_source()
    import_pattern = re.compile(r"^import\s+([\w.]+);", re.MULTILINE)
    imports = import_pattern.findall(src)
    assert len(imports) > 0, "No import statements found"
    for imp in imports:
        parts = imp.split(".")
        for part in parts:
            assert re.match(r"^[a-zA-Z_]\w*$", part), f"Invalid identifier in import: {part}"
    assert any("org.apache.flink" in imp for imp in imports), "Missing Flink imports"
    assert any("org.apache.beam" in imp for imp in imports), "Missing Beam imports"


# [static] pass_to_pass
def test_java_class_structure_valid():
    """Target Java file has valid class structure with proper nesting (pass_to_pass)."""
    src = _read_source()
    class_match = re.search(
        r"public\s+class\s+LazyFlinkSourceSplitEnumerator<([^>]+)>\s+implements\s+([^\{]+)",
        src
    )
    assert class_match, "Class declaration with generics and implements not found"
    class_start = src.find("public class LazyFlinkSourceSplitEnumerator")
    assert class_start != -1, "Class start not found"
    brace_start = src.find("{", class_start)
    assert brace_start != -1, "Opening brace not found after class declaration"
    brace_count = 1
    pos = brace_start + 1
    while pos < len(src) and brace_count > 0:
        if src[pos] == "{": brace_count += 1
        elif src[pos] == "}": brace_count -= 1
        pos += 1
    assert brace_count == 0, "Class body has unbalanced braces"
    class_body = src[brace_start:pos]
    assert re.search(r"private\s+\w+", class_body), "No private fields found"
    assert re.search(r"public\s+LazyFlinkSourceSplitEnumerator\s*\(", src), "Constructor not found"
    assert re.search(r"public\s+void\s+handleSplitRequest\s*\(", src), "handleSplitRequest method declaration invalid"
    assert re.search(r"public\s+void\s+initializeSplits\s*\(", src), "initializeSplits method declaration invalid"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral tests
#
# These tests verify BEHAVIOR by checking for proper synchronization patterns.
# They accept ANY correct concurrent primitive, not just the gold-specific one.
#
# Alternative correct fixes that MUST pass:
#   Fix 1: CountDownLatch (await/countDown) + volatile boolean
#   Fix 2: Semaphore (acquire/release) + volatile boolean
#   Fix 3: Lock + Condition (lock/await/unlock.signalAll)
#   Fix 4: CompletableFuture (join/complete) -- callback sets splitsInitialized
# ---------------------------------------------------------------------------

def _extract_method(src, method_name):
    """Extract a Java method body by name using brace-counting."""
    pattern = re.compile(
        rf"(?:public|private|protected|\s)+[\w<>,\s\[\]?@]*\s+{method_name}\s*\([^)]*\)[^{{]*\{{",
        re.DOTALL,
    )
    match = pattern.search(src)
    if not match:
        return ""
    brace_count = 0
    for i in range(match.end() - 1, len(src)):
        if src[i] == "{": brace_count += 1
        elif src[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                return src[match.start() : i + 1]
    return src[match.start() :]


def _has_blocking_mechanism(method_body):
    """Check if method contains ANY valid blocking mechanism for concurrent coordination."""
    blocking_patterns = [
        r"\.await\s*\(",
        r"\.get\s*\(",
        r"\.join\s*\(",
        r"\.acquire\s*\(",
        r"LockSupport\.park",
    ]
    if re.search(r"synchronized", method_body) and re.search(r"\.wait\s*\(", method_body):
        return True
    return any(re.search(p, method_body) for p in blocking_patterns)


def _has_finally_with_signal(method_body):
    """Check if method has a finally block that signals completion."""
    finally_match = re.search(
        r"finally\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
        method_body, re.DOTALL
    )
    if not finally_match:
        return False
    finally_body = finally_match.group(1)
    signal_patterns = [
        r"\.countDown\s*\(",
        r"\.release\s*\(",
        r"\.signalAll?\s*\(",
        r"\.complete\s*\(",
        r"\.unlock\s*\(",
        r"\.notify",
        r"LockSupport\.unpark",
    ]
    return any(re.search(p, finally_body) for p in signal_patterns)


def _has_thread_safe_visibility(src):
    """Check if splitsInitialized has thread-safe visibility mechanism."""
    if re.search(r"volatile\s+boolean\s+splitsInitialized", src):
        return True
    if re.search(r"AtomicBoolean\s+splitsInitialized", src):
        return True
    if re.search(r"synchronized", src) and re.search(r"\.unlock\s*\(", src):
        return True
    return False


# [pr_diff] fail_to_pass
def test_handle_split_request_blocks_on_uninitialized():
    """handleSplitRequest must block/wait until splits initialization completes."""
    src = _read_source()
    method = _extract_method(src, "handleSplitRequest")
    assert method, "handleSplitRequest method not found"
    assert _has_blocking_mechanism(method), (
        "handleSplitRequest must block until initialization completes. "
        "Expected some blocking call: latch.await(), semaphore.acquire(), "
        "condition.await(), future.get(), lock.await(), park(), etc."
    )


# [pr_diff] fail_to_pass
def test_splits_initialized_thread_safe():
    """splitsInitialized must be visible across threads."""
    src = _read_source()
    assert _has_thread_safe_visibility(src), (
        "splitsInitialized must be visible across threads: "
        "use volatile boolean, AtomicBoolean, or synchronized blocks"
    )


# [pr_diff] fail_to_pass
def test_initialization_signals_in_finally():
    """initializeSplits must signal completion in a finally block."""
    src = _read_source()
    method = _extract_method(src, "initializeSplits")
    assert method, "initializeSplits method not found"
    assert _has_finally_with_signal(method), (
        "initializeSplits must signal completion in a finally block to prevent "
        "deadlock on error. Use countDown(), release(), signal(), complete(), "
        "unlock(), notify(), unpark(), etc."
    )


# [pr_diff] fail_to_pass
def test_synchronization_fix_java_validation():
    """Java file must import a java.util.concurrent synchronization primitive."""
    src = _read_source()
    concurrent_imports = [
        r"import\s+java\.util\.concurrent\.CountDownLatch",
        r"import\s+java\.util\.concurrent\.Semaphore",
        r"import\s+java\.util\.concurrent\.CompletableFuture",
        r"import\s+java\.util\.concurrent\.locks\.",
        r"import\s+java\.util\.concurrent\.atomic\.AtomicBoolean",
    ]
    has_concurrent = any(re.search(p, src) for p in concurrent_imports)
    assert has_concurrent, (
        "Must import a java.util.concurrent synchronization primitive "
        "(CountDownLatch, Semaphore, CompletableFuture, locks, or AtomicBoolean)"
    )


# [static] pass_to_pass
def test_java_no_syntax_errors():
    """Target Java file has no obvious syntax errors (pass_to_pass)."""
    src = _read_source()
    field_pattern = re.compile(r"(?:private|public|protected)\s+(?:\w+\s+)*(\w+)\s+\w+\s*[=;]")
    for match in field_pattern.finditer(src):
        type_name = match.group(1)
        assert re.match(r"^[a-zA-Z_]\w*$", type_name), f"Invalid type name: {type_name}"
    assert not re.search(r"catch\s*\([^)]+\)\s*\{\s*\}", src), "Empty catch block found"
    assert src.count("{") == src.count("}"), f"Unbalanced braces"
    assert ";;" not in src, "Double semicolon found"
    assert re.search(r"^package\s+[\w.]+;", src, re.MULTILINE), "Package declaration not found or invalid"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI/CD tests that run actual repo commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_apache_license_header():
    """Target Java file has Apache License 2.0 header (pass_to_pass)."""
    r = subprocess.run(["grep", "-q", "Licensed to the Apache Software Foundation", TARGET_FILE], capture_output=True)
    assert r.returncode == 0, f"Apache License header not found in {TARGET_FILE}"


# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Git repository is valid with expected file state (pass_to_pass)."""
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    allowed = ["?? /logs", "M runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java"]
    unexpected = [l for l in lines if not any(l.startswith(p) or l == p for p in allowed)]
    assert len(unexpected) == 0, f"Repository has unexpected changes: {unexpected}"


# [repo_tests] pass_to_pass
def test_repo_target_file_exists():
    """Target file exists at expected path (pass_to_pass)."""
    r = subprocess.run(["test", "-f", TARGET_FILE], capture_output=True)
    assert r.returncode == 0, f"Target file not found: {TARGET_FILE}"


# [repo_tests] pass_to_pass
def test_repo_java_package_structure():
    """Java package declaration matches directory structure (pass_to_pass)."""
    r = subprocess.run(["grep", "-q", "^package org.apache.beam.runners.flink.translation.wrappers.streaming.io.source;", TARGET_FILE], capture_output=True)
    assert r.returncode == 0, "Package declaration doesn't match expected"


# [repo_tests] pass_to_pass
def test_repo_file_has_class_declaration():
    """Target file contains valid public class declaration (pass_to_pass)."""
    r = subprocess.run(["grep", "-q", r"public class LazyFlinkSourceSplitEnumerator", TARGET_FILE], capture_output=True)
    assert r.returncode == 0, "Public class declaration not found in target file"
