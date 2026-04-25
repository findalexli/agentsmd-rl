"""
Tests for Selenium PR #17257: OSGi Resource Loading Fix

Structural tests that verify:
1. The new resourceAsString(Class<?>, String) method exists
2. The old method is deprecated and delegates to new
3. Caller classes are updated to use the new method
4. Basic Java syntax is valid
"""

import re
from pathlib import Path

REPO = "/workspace/selenium"


# =============================================================================
# FAIL_TO_PASS: Core structural tests - verify code patterns
# =============================================================================

def test_new_method_signature_exists():
    """
    Verify Read.java has the new resourceAsString(Class<?>, String) method.
    (fail_to_pass) - This method doesn't exist in the base commit.
    """
    read_java = Path(REPO) / "java/src/org/openqa/selenium/io/Read.java"
    content = read_java.read_text()

    # Check for the new method signature
    pattern = r'public\s+static\s+String\s+resourceAsString\s*\(\s*Class<\?>\s+\w+\s*,\s*String\s+\w+\s*\)'
    match = re.search(pattern, content)
    assert match is not None, (
        "Read.java must have method signature: "
        "public static String resourceAsString(Class<?> resourceOwner, String resource)"
    )


def test_old_method_deprecated():
    """
    Verify the old resourceAsString(String) method is marked @Deprecated.
    (fail_to_pass) - The old method is not deprecated in the base commit.
    """
    read_java = Path(REPO) / "java/src/org/openqa/selenium/io/Read.java"
    content = read_java.read_text()

    # Look for @Deprecated annotation before resourceAsString(String resource)
    pattern = r'@Deprecated[^}]*?public\s+static\s+String\s+resourceAsString\s*\(\s*String\s+\w+\s*\)'
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, (
        "The old resourceAsString(String) method must be annotated with @Deprecated"
    )


def test_old_method_delegates_to_new():
    """
    Verify the old method delegates to the new method with Read.class.
    (fail_to_pass) - In base commit, old method directly calls getResourceAsStream.
    """
    read_java = Path(REPO) / "java/src/org/openqa/selenium/io/Read.java"
    content = read_java.read_text()

    # The old method should now contain: return resourceAsString(Read.class, resource);
    pattern = r'public\s+static\s+String\s+resourceAsString\s*\(\s*String\s+\w+\s*\)\s*\{[^}]*resourceAsString\s*\(\s*Read\.class'
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, (
        "The old resourceAsString(String) method must delegate to resourceAsString(Read.class, resource)"
    )


def test_cdp_event_types_uses_class_parameter():
    """
    Verify CdpEventTypes.java uses the new two-argument resourceAsString method.
    (fail_to_pass) - In base commit, it uses the single-argument version.
    """
    cdp_file = Path(REPO) / "java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java"
    content = cdp_file.read_text()

    # Check that it uses resourceAsString with CdpEventTypes.class as first argument
    pattern = r'Read\.resourceAsString\s*\(\s*CdpEventTypes\.class\s*,'
    match = re.search(pattern, content)
    assert match is not None, (
        "CdpEventTypes.java must call Read.resourceAsString with CdpEventTypes.class as first argument"
    )


def test_remote_script_uses_class_parameter():
    """
    Verify RemoteScript.java uses the new two-argument resourceAsString method.
    (fail_to_pass) - In base commit, it uses the single-argument version.
    """
    remote_script = Path(REPO) / "java/src/org/openqa/selenium/remote/RemoteScript.java"
    content = remote_script.read_text()

    # Check that it uses resourceAsString with getClass() as first argument
    pattern = r'Read\.resourceAsString\s*\(\s*getClass\(\)\s*,'
    match = re.search(pattern, content)
    assert match is not None, (
        "RemoteScript.java must call Read.resourceAsString with getClass() as first argument"
    )


def test_w3c_codec_uses_class_parameter():
    """
    Verify W3CHttpCommandCodec.java uses the new two-argument resourceAsString method.
    (fail_to_pass) - In base commit, it uses the single-argument version.
    """
    codec_file = Path(REPO) / "java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java"
    content = codec_file.read_text()

    # Check that it uses resourceAsString with getClass() as first argument
    pattern = r'resourceAsString\s*\(\s*getClass\(\)\s*,'
    match = re.search(pattern, content)
    assert match is not None, (
        "W3CHttpCommandCodec.java must call resourceAsString with getClass() as first argument"
    )


def test_read_test_updated():
    """
    Verify ReadTest.java uses the new two-argument resourceAsString method.
    (fail_to_pass) - In base commit, test uses single-argument version.
    """
    test_file = Path(REPO) / "java/test/org/openqa/selenium/io/ReadTest.java"
    content = test_file.read_text()

    # Check that test calls Read.resourceAsString(Read.class, "...")
    pattern = r'Read\.resourceAsString\s*\(\s*Read\.class\s*,'
    match = re.search(pattern, content)
    assert match is not None, (
        "ReadTest.java must call Read.resourceAsString with Read.class as first argument"
    )


# =============================================================================
# PASS_TO_PASS: Syntax validation - must pass before and after fix
# =============================================================================

def test_java_syntax_valid():
    """
    Verify Read.java has valid Java syntax by checking basic structure.
    (pass_to_pass) - Should pass both before and after fix.
    """
    read_java = Path(REPO) / "java/src/org/openqa/selenium/io/Read.java"
    content = read_java.read_text()

    # Basic syntax checks
    assert "package org.openqa.selenium.io;" in content, "Package declaration missing"
    assert "public class Read" in content or "public final class Read" in content, "Class declaration missing"
    assert content.count("{") == content.count("}"), "Mismatched braces in Read.java"


def test_cdp_event_types_syntax_valid():
    """
    Verify CdpEventTypes.java has valid Java syntax.
    (pass_to_pass) - Should pass both before and after fix.
    """
    cdp_file = Path(REPO) / "java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java"
    content = cdp_file.read_text()

    assert "package org.openqa.selenium.devtools.events;" in content, "Package declaration missing"
    assert "class CdpEventTypes" in content, "Class declaration missing"
    assert content.count("{") == content.count("}"), "Mismatched braces"
