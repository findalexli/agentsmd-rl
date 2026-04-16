"""Tests for CoreProgressManager.java fix to avoid sun.misc.Unsafe usage."""

import subprocess
import re
import os

REPO = "/workspace/kotlin"
TARGET_FILE = os.path.join(REPO, "compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java")


def read_file():
    """Read the target Java file."""
    with open(TARGET_FILE, 'r') as f:
        return f.read()


def test_no_java11shim_import():
    """Java11Shim import should be removed (F2P)."""
    content = read_file()
    assert "import com.intellij.util.Java11Shim;" not in content, \
        "Java11Shim import should be removed"


def test_no_concurrentlongobjectmap_import():
    """ConcurrentLongObjectMap import should be removed (F2P)."""
    content = read_file()
    assert "import com.intellij.util.containers.ConcurrentLongObjectMap;" not in content, \
        "ConcurrentLongObjectMap import should be removed"


def test_no_concurrentlongobjectmap_field_type_currentindicators():
    """currentIndicators field should not use ConcurrentLongObjectMap (F2P).

    The bug is that ConcurrentLongObjectMap relies on sun.misc.Unsafe.
    Any correct fix must stop using this type for currentIndicators.
    """
    content = read_file()
    assert "ConcurrentLongObjectMap<ProgressIndicator> currentIndicators" not in content, \
        "currentIndicators should not use ConcurrentLongObjectMap (uses sun.misc.Unsafe)"


def test_no_concurrentlongobjectmap_field_type_threadtoplevelindicators():
    """threadTopLevelIndicators field should not use ConcurrentLongObjectMap (F2P).

    The bug is that ConcurrentLongObjectMap relies on sun.misc.Unsafe.
    Any correct fix must stop using this type for threadTopLevelIndicators.
    """
    content = read_file()
    assert "ConcurrentLongObjectMap<ProgressIndicator> threadTopLevelIndicators" not in content, \
        "threadTopLevelIndicators should not use ConcurrentLongObjectMap (uses sun.misc.Unsafe)"


def test_no_java11shim_usage_for_currentindicators():
    """Java11Shim should not be used to create currentIndicators map (F2P)."""
    content = read_file()
    assert "Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap()" not in content, \
        "Should not use Java11Shim to create currentIndicators"


def test_no_java11shim_usage_for_threadtoplevelindicators():
    """Java11Shim should not be used to create threadTopLevelIndicators map (F2P)."""
    content = read_file()
    assert "Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap()" not in content, \
        "Should not use Java11Shim to create threadTopLevelIndicators"


def test_concurrentmap_import_present():
    """ConcurrentMap should be available (via java.util.concurrent.*) (F2P).

    The fix requires using java.util.concurrent.* types to avoid sun.misc.Unsafe.
    """
    content = read_file()
    assert "import java.util.concurrent.*;" in content, \
        "java.util.concurrent.* should be imported"


def test_concurrent_map_type_is_used():
    """ConcurrentMap<Long, ProgressIndicator> type should appear (F2P).

    A correct fix must use a ConcurrentMap type with Long keys for the indicator maps.
    This substring appears in field declarations, method signatures, or casts
    whenever ConcurrentMap<Long, ProgressIndicator> is used.
    """
    content = read_file()
    assert "ConcurrentMap<Long, ProgressIndicator>" in content, \
        "ConcurrentMap<Long, ProgressIndicator> type should be used for thread-safe map"


def test_java_braces_balanced():
    """Java file should have balanced braces (P2P)."""
    content = read_file()
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"

    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    open_brackets = content.count('[')
    close_brackets = content.count(']')
    assert open_brackets == close_brackets, \
        f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"


def test_class_declaration_intact():
    """Class declaration should remain intact (P2P)."""
    content = read_file()
    assert "public class CoreProgressManager extends ProgressManager implements Disposable" in content, \
        "Class declaration should be intact"


def test_fields_count_unchanged():
    """Number of static fields should be unchanged (P2P)."""
    content = read_file()
    static_final_fields = re.findall(r'private static final \w+', content)
    assert len(static_final_fields) >= 4, \
        f"Expected at least 4 static final fields, found {len(static_final_fields)}"


def test_repo_java_syntax():
    """Java file should have valid syntax for basic structure (pass_to_pass)."""
    r = subprocess.run(
        ["javac", "-d", "/tmp/compiled", "-sourcepath", f"{REPO}/compiler/cli/src", TARGET_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    stderr_lower = r.stderr.lower()
    syntax_errors = [
        "expected", "unexpected", "illegal start", "unclosed", "reached end",
        "missing", "invalid method declaration", "not a statement"
    ]
    for err in syntax_errors:
        assert err not in stderr_lower, f"Java syntax error detected: {err}\n{r.stderr[:1000]}"


def test_repo_no_sun_misc_unsafe():
    """sun.misc.Unsafe should not appear in executable code (pass_to_pass)."""
    content = read_file()
    # Remove single-line comments
    code_only = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    # Remove multi-line comments
    code_only = re.sub(r'/\*.*?\*/', '', code_only, flags=re.DOTALL)
    assert "sun.misc.Unsafe" not in code_only, \
        "sun.misc.Unsafe should only be mentioned in comments, not actual code usage"


def test_repo_package_declaration():
    """Package declaration should be present and correct (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-n", "^package com.intellij.openapi.progress.impl;", TARGET_FILE],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, "Package declaration should be present"
    assert "package com.intellij.openapi.progress.impl;" in r.stdout
