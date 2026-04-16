"""
Tests for SeleniumHQ/selenium#17225: Add field names to JsonException error messages.

The PR improves error messages when duplicate JSON field names are detected by
including the conflicting field names (e.g., "FieldWriter(ClassName.fieldName)")
instead of just "Duplicate JSON field name detected".
"""

import subprocess
import os
import re
from pathlib import Path

REPO = Path("/workspace/selenium")

# Java test source that triggers the duplicate field detection
TEST_JAVA_SOURCE = '''
package test;

import org.openqa.selenium.json.Json;
import org.openqa.selenium.json.JsonException;
import org.openqa.selenium.json.PropertySetting;

public class DuplicateFieldTest {
    // Parent class with a "value" field
    public static class ParentBean {
        public String value;
    }

    // Child class with its own "value" field - creates duplicate
    public static class ChildBean extends ParentBean {
        public String value;
    }

    // Another parent-child pair for variation
    public static class ParentItem {
        public int count;
    }

    public static class ChildItem extends ParentItem {
        public int count;
    }

    public static void main(String[] args) {
        String testType = args.length > 0 ? args[0] : "exception_has_field_names";

        switch (testType) {
            case "exception_has_field_names":
                testExceptionHasFieldNames();
                break;
            case "exception_has_field_names_variation":
                testExceptionHasFieldNamesVariation();
                break;
            case "parent_class_works":
                testParentClassWorks();
                break;
            default:
                System.err.println("Unknown test: " + testType);
                System.exit(1);
        }
    }

    private static void testExceptionHasFieldNames() {
        Json json = new Json();
        String rawJson = "{\\"value\\": \\"test\\"}";

        try {
            json.toType(rawJson, ChildBean.class, PropertySetting.BY_FIELD);
            System.out.println("FAIL: Expected JsonException but none was thrown");
            System.exit(1);
        } catch (JsonException e) {
            String causeMsg = e.getCause() != null ? e.getCause().getMessage() : "";

            // Check that the message includes "FieldWriter" format with class and field names
            if (causeMsg.contains("FieldWriter") &&
                causeMsg.contains("ChildBean.value") &&
                causeMsg.contains("ParentBean.value")) {
                System.out.println("PASS: Exception message includes field names");
                System.out.println("Message: " + causeMsg);
            } else {
                System.out.println("FAIL: Exception message does not include proper field names");
                System.out.println("Expected format: FieldWriter(...ChildBean.value) vs FieldWriter(...ParentBean.value)");
                System.out.println("Actual message: " + causeMsg);
                System.exit(1);
            }
        }
    }

    private static void testExceptionHasFieldNamesVariation() {
        Json json = new Json();
        String rawJson = "{\\"count\\": 42}";

        try {
            json.toType(rawJson, ChildItem.class, PropertySetting.BY_FIELD);
            System.out.println("FAIL: Expected JsonException but none was thrown");
            System.exit(1);
        } catch (JsonException e) {
            String causeMsg = e.getCause() != null ? e.getCause().getMessage() : "";

            // Check that the message includes "FieldWriter" format with class and field names
            if (causeMsg.contains("FieldWriter") &&
                causeMsg.contains("ChildItem.count") &&
                causeMsg.contains("ParentItem.count")) {
                System.out.println("PASS: Exception message includes field names (variation)");
                System.out.println("Message: " + causeMsg);
            } else {
                System.out.println("FAIL: Exception message does not include proper field names");
                System.out.println("Expected format: FieldWriter(...ChildItem.count) vs FieldWriter(...ParentItem.count)");
                System.out.println("Actual message: " + causeMsg);
                System.exit(1);
            }
        }
    }

    private static void testParentClassWorks() {
        Json json = new Json();
        String rawJson = "{\\"value\\": \\"hello\\"}";

        ParentBean result = json.toType(rawJson, ParentBean.class, PropertySetting.BY_FIELD);
        if ("hello".equals(result.value)) {
            System.out.println("PASS: Parent class parsing works correctly");
        } else {
            System.out.println("FAIL: Expected value='hello', got: " + result.value);
            System.exit(1);
        }
    }
}
'''


JSPECIFY_JAR = Path("/workspace/libs/jspecify-1.0.0.jar")


def compile_json_module():
    """Compile the Selenium json module and test class."""
    json_src = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json"
    internal_src = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "internal"

    # Create output directory
    out_dir = REPO / "test_build"
    out_dir.mkdir(exist_ok=True)

    # Write test source
    test_dir = out_dir / "test"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "DuplicateFieldTest.java").write_text(TEST_JAVA_SOURCE)

    # Find all Java files to compile
    json_files = list(json_src.glob("*.java"))
    internal_files = list(internal_src.glob("*.java"))

    all_files = json_files + internal_files + [test_dir / "DuplicateFieldTest.java"]

    # Compile with jspecify dependency
    cmd = [
        "javac",
        "-d", str(out_dir),
        "-cp", str(JSPECIFY_JAR),
        "-sourcepath", str(REPO / "java" / "src") + ":" + str(out_dir),
    ] + [str(f) for f in all_files]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode == 0, result.stderr


def run_java_test(test_name):
    """Run a Java test and return (success, output)."""
    out_dir = REPO / "test_build"

    cmd = [
        "java",
        "-cp", f"{out_dir}:{JSPECIFY_JAR}",
        "test.DuplicateFieldTest",
        test_name
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0, result.stdout + result.stderr


def test_java_compiles():
    """The Java code compiles without errors (pass_to_pass)."""
    success, stderr = compile_json_module()
    assert success, f"Compilation failed:\n{stderr}"


def test_exception_message_contains_field_names():
    """
    Exception message includes field names in 'FieldWriter(ClassName.fieldName)' format (fail_to_pass).

    Before the fix, the exception just said:
      "Duplicate JSON field name detected while collecting field writers"

    After the fix, it says:
      "Duplicate JSON field name detected while collecting field writers:
       FieldWriter(ChildBean.value) vs FieldWriter(ParentBean.value)"
    """
    # Ensure compiled
    compile_json_module()

    success, output = run_java_test("exception_has_field_names")
    assert success, f"Test failed:\n{output}"
    assert "PASS" in output, f"Test did not pass:\n{output}"


def test_exception_message_contains_field_names_variation():
    """
    Exception message includes field names with different field/class names (fail_to_pass).

    Tests with a different parent/child class pair to ensure the fix is not hardcoded.
    """
    # Ensure compiled
    compile_json_module()

    success, output = run_java_test("exception_has_field_names_variation")
    assert success, f"Test failed:\n{output}"
    assert "PASS" in output, f"Test did not pass:\n{output}"


def test_parent_class_parsing_still_works():
    """Parent class without duplicate fields still parses correctly (pass_to_pass)."""
    # Ensure compiled
    compile_json_module()

    success, output = run_java_test("parent_class_works")
    assert success, f"Test failed:\n{output}"
    assert "PASS" in output, f"Test did not pass:\n{output}"


def test_fieldwriter_class_exists():
    """
    The FieldWriter inner class exists with a toString method (fail_to_pass).

    The fix introduces a named FieldWriter class to replace the anonymous lambda,
    which provides a meaningful toString() for error messages.
    """
    instance_coercer = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json" / "InstanceCoercer.java"
    content = instance_coercer.read_text()

    # Check for FieldWriter class definition
    assert "class FieldWriter implements BiConsumer" in content, \
        "FieldWriter class not found - should implement BiConsumer<Object, Object>"

    # Check that FieldWriter has a toString method
    assert re.search(r'class\s+FieldWriter.*?public\s+String\s+toString\s*\(\s*\)', content, re.DOTALL), \
        "FieldWriter.toString() method not found"


def test_simple_property_descriptor_has_tostring():
    """
    SimplePropertyDescriptor has a toString method (fail_to_pass).

    The fix adds a toString() to SimplePropertyDescriptor that returns
    "ClassName.propertyName" format for better error messages.
    """
    descriptor_file = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json" / "SimplePropertyDescriptor.java"
    content = descriptor_file.read_text()

    # Check for toString override
    assert "@Override" in content and "public String toString()" in content, \
        "SimplePropertyDescriptor should have a toString() override"

    # Check the toString implementation format
    assert 'clazz.getSimpleName()' in content or 'getSimpleName()' in content, \
        "toString() should use class simple name for readable output"


def test_simple_property_descriptor_constructor_takes_class():
    """
    SimplePropertyDescriptor constructor accepts Class<?> parameter (fail_to_pass).

    The fix adds a clazz parameter to store the declaring class for toString().
    """
    descriptor_file = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json" / "SimplePropertyDescriptor.java"
    content = descriptor_file.read_text()

    # Check that constructor takes Class<?> clazz parameter
    assert re.search(r'public\s+SimplePropertyDescriptor\s*\(\s*Class<\?>\s+clazz', content), \
        "SimplePropertyDescriptor constructor should take Class<?> clazz as first parameter"

    # Check that the clazz field is stored
    assert "private final Class<?> clazz" in content or "private final Class<?> clazz;" in content, \
        "SimplePropertyDescriptor should have a 'clazz' field to store the class"


# =============================================================================
# Pass-to-pass tests: These should pass on BOTH base and fixed commits
# =============================================================================


def test_json_module_compiles_standalone():
    """
    The JSON module compiles as a standalone unit without test dependencies (pass_to_pass).

    This verifies the module has no missing imports or circular dependencies
    that would prevent compilation.
    """
    json_src = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json"
    internal_src = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "internal"

    # Get all Java files in the json module
    json_files = list(json_src.glob("*.java"))
    internal_files = list(internal_src.glob("*.java"))

    all_files = json_files + internal_files

    cmd = [
        "javac",
        "-d", "/tmp/json_standalone",
        "-cp", str(JSPECIFY_JAR),
        "-sourcepath", str(REPO / "java" / "src"),
    ] + [str(f) for f in all_files]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, f"JSON module compilation failed:\n{result.stderr[-1000:]}"


def test_modified_files_have_valid_java_syntax():
    """
    The modified files have valid Java syntax and compile successfully (pass_to_pass).

    Specifically compiles InstanceCoercer.java and SimplePropertyDescriptor.java
    which are the files modified in this PR.
    """
    modified_files = [
        REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json" / "InstanceCoercer.java",
        REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json" / "SimplePropertyDescriptor.java",
    ]

    # Verify files exist
    for f in modified_files:
        assert f.exists(), f"Modified file not found: {f}"

    # Compile just these files with their dependencies
    cmd = [
        "javac",
        "-d", "/tmp/modified_check",
        "-cp", str(JSPECIFY_JAR),
        "-sourcepath", str(REPO / "java" / "src"),
    ] + [str(f) for f in modified_files]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, f"Modified files compilation failed:\n{result.stderr[-500:]}"


def test_json_files_use_lf_line_endings():
    """
    All Java files in the JSON module use LF line endings (pass_to_pass).

    Per .editorconfig, all files should use end_of_line = lf.
    This is a static check for code consistency.
    """
    json_src = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json"

    for java_file in json_src.glob("*.java"):
        content = java_file.read_bytes()
        # Check for CRLF (Windows line endings)
        if b'\r\n' in content:
            assert False, f"File {java_file.name} has CRLF line endings, expected LF"
        # Check for CR only (old Mac line endings)
        if b'\r' in content and b'\r\n' not in content:
            assert False, f"File {java_file.name} has CR line endings, expected LF"


def test_json_files_have_final_newline():
    """
    All Java files in the JSON module end with a newline (pass_to_pass).

    Per .editorconfig, all files should have insert_final_newline = true.
    This is a static check for code consistency.
    """
    json_src = REPO / "java" / "src" / "org" / "openqa" / "selenium" / "json"

    for java_file in json_src.glob("*.java"):
        content = java_file.read_bytes()
        if not content.endswith(b'\n'):
            assert False, f"File {java_file.name} does not end with a newline"
