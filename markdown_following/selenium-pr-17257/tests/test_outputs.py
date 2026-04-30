"""
Tests for Selenium PR #17257: OSGi Resource Loading Fix.

Behavioral tests (subprocess.run with javac/java) verify:
1. The class-aware resource loading API compiles and works at runtime
2. Read.java itself compiles cleanly (pass-to-pass regression guard)

Structural tests verify callers have been updated to use class-aware loading.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/selenium"


# =============================================================================
# FAIL_TO_PASS: Behavioral - class-aware API exists and works
# =============================================================================

def test_class_aware_method_compiles_and_loads():
    """
    Verify the class-aware resource loading API compiles and loads resources.

    On base: a harness calling resourceAsString with a class parameter
    fails to compile because only the single-argument method exists.
    On gold: the harness compiles, runs, and successfully loads a resource.
    """
    # Compile Read.java
    r = subprocess.run(
        ["bash", "-lc",
         "cd /workspace/selenium && "
         "javac -d /tmp/cls1 java/src/org/openqa/selenium/io/Read.java 2>&1"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Read.java compilation failed: {r.stderr}"

    # Create a test resource on the classpath
    resource_dir = Path("/tmp/cls1/org/openqa/selenium/remote")
    resource_dir.mkdir(parents=True, exist_ok=True)
    (resource_dir / "test_resource.js").write_text(
        "function testHelper() { return 'class-aware-loaded'; }\n"
    )

    # Write a harness that uses class-aware resource loading
    harness = (
        "import org.openqa.selenium.io.Read;\n"
        "public class ClassAwareHarness {\n"
        "    public static void main(String[] args) throws Exception {\n"
        '        String result = Read.resourceAsString('
        "ClassAwareHarness.class, args[0]);\n"
        "        if (result == null || result.isEmpty()) {\n"
        '            throw new RuntimeException("Resource was empty");\n'
        "        }\n"
        '        if (!result.contains("testHelper")) {\n'
        '            throw new RuntimeException('
        '"Missing expected content, got: " + result.substring(0, Math.min(80, result.length())));\n'
        "        }\n"
        '        System.out.println("CLASS_AWARE_OK");\n'
        "    }\n"
        "}\n"
    )
    Path("/tmp/ClassAwareHarness.java").write_text(harness)

    # Compile harness against Read.class + resource directory
    r = subprocess.run(
        ["bash", "-lc",
         "javac -cp /tmp/cls1 -d /tmp/cls1 /tmp/ClassAwareHarness.java 2>&1"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Harness compilation failed - class-aware resourceAsString may be missing. "
        f"stderr: {r.stderr}"
    )

    # Run the harness
    r = subprocess.run(
        ["bash", "-lc",
         "cd /workspace/selenium && "
         "java -cp /tmp/cls1 ClassAwareHarness "
         "/org/openqa/selenium/remote/test_resource.js 2>&1"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Resource loading failed: {r.stderr}\n{r.stdout}"
    assert "CLASS_AWARE_OK" in r.stdout, (
        "Class-aware resource loading did not produce expected output"
    )


# =============================================================================
# FAIL_TO_PASS: Structural - callers updated to use class-aware loading
# =============================================================================

def test_callers_use_class_aware_loading():
    """
    Verify all caller classes have been updated to use class-aware
    resource loading (two-argument form with a class or getClass()).

    On base: callers use single-argument resourceAsString.
    On gold: callers specify a class to use for classloader resolution.
    """
    cdp_file = Path(REPO) / "java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java"
    remote_file = Path(REPO) / "java/src/org/openqa/selenium/remote/RemoteScript.java"
    codec_file = Path(REPO) / "java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java"
    test_file = Path(REPO) / "java/test/org/openqa/selenium/io/ReadTest.java"

    # CdpEventTypes must use CdpEventTypes.class as first argument
    cdp_content = cdp_file.read_text()
    assert re.search(
        r'Read\.resourceAsString\s*\(\s*CdpEventTypes\.class\s*,', cdp_content
    ), "CdpEventTypes.java must pass CdpEventTypes.class to resourceAsString"

    # RemoteScript must use getClass() as first argument
    remote_content = remote_file.read_text()
    assert re.search(
        r'Read\.resourceAsString\s*\(\s*getClass\(\)\s*,', remote_content
    ), "RemoteScript.java must pass getClass() to resourceAsString"

    # W3CHttpCommandCodec must use getClass() as first argument
    codec_content = codec_file.read_text()
    assert re.search(
        r'resourceAsString\s*\(\s*getClass\(\)\s*,', codec_content
    ), "W3CHttpCommandCodec.java must pass getClass() to resourceAsString"

    # ReadTest must use Read.class as first argument
    test_content = test_file.read_text()
    assert re.search(
        r'Read\.resourceAsString\s*\(\s*Read\.class\s*,', test_content
    ), "ReadTest.java must pass Read.class to resourceAsString"


# =============================================================================
# PASS_TO_PASS: Behavioral - basic compilation regression guard
# =============================================================================

def test_read_java_compiles():
    """
    Verify Read.java compiles without errors. This must pass on both
    the base and gold commits - the fix must not break compilation.
    """
    r = subprocess.run(
        ["bash", "-lc",
         "cd /workspace/selenium && "
         "javac -d /tmp/cls_ptp1 java/src/org/openqa/selenium/io/Read.java 2>&1"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Read.java had compilation errors: {r.stderr}"


# =============================================================================
# PASS_TO_PASS: Structural - basic syntax validity
# =============================================================================

def test_java_files_syntax_valid():
    """
    Verify basic Java syntax validity (brace balance, declarations)
    for key files. Must pass both before and after the fix.
    """
    read_java = Path(REPO) / "java/src/org/openqa/selenium/io/Read.java"
    cdp_file = Path(REPO) / "java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java"

    for path in [read_java, cdp_file]:
        content = path.read_text()
        assert content.count("{") == content.count("}"), (
            f"Mismatched braces in {path.name}"
        )
        assert "class " in content, f"Class declaration missing in {path.name}"

    # Read.java specific: must have its package and class declarations
    read_content = read_java.read_text()
    assert "package org.openqa.selenium.io;" in read_content, (
        "Read.java missing package declaration"
    )
    assert "public class Read" in read_content or "public final class Read" in read_content, (
        "Read.java missing class declaration"
    )

    # CdpEventTypes.java specific: must have its package and class declarations
    cdp_content = cdp_file.read_text()
    assert "package org.openqa.selenium.devtools.events;" in cdp_content, (
        "CdpEventTypes.java missing package declaration"
    )
    assert "class CdpEventTypes" in cdp_content, (
        "CdpEventTypes.java missing class declaration"
    )
