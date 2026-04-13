#!/usr/bin/env python3
"""Tests for Selenium JSON duplicate field exception improvements.

This task requires improving error messages in InstanceCoercer.java and
SimplePropertyDescriptor.java to include field names when duplicate JSON
field names are detected during deserialization.
"""

import subprocess
import re
import os

REPO = "/workspace/selenium"


def run_bazel_test(test_target, timeout=300):
    """Run a bazel test and return the result."""
    result = subprocess.run(
        ["bazel", "test", test_target, "--test_output=all", "--test_size_filters=small"],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO
    )
    return result


def test_duplicate_field_error_message_includes_field_names():
    """Test that duplicate field exception includes field names in the message.

    When deserializing JSON to a class that inherits a field with the same name
    from a parent class, the error message should identify which fields are
    in conflict (e.g., ChildFieldBean.value vs ParentFieldBean.value).
    """
    # Run the specific test that checks this behavior
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")

    # The test should pass, meaning the error message now includes field names
    assert result.returncode == 0, (
        f"JsonTest failed. Expected test to pass with improved error messages.\n"
        f"STDOUT: {result.stdout[-2000:]}\n"
        f"STDERR: {result.stderr[-2000:]}"
    )


def test_error_message_contains_fieldwriter_info():
    """Verify the error message format includes class and field names.

    The fix should change the error message from:
    "Duplicate JSON field name detected while collecting field writers"
    to:
    "Duplicate JSON field name detected while collecting field writers:
     FieldWriter(org.openqa.selenium.json.JsonTest\$ChildFieldBean.value) vs
     FieldWriter(org.openqa.selenium.json.JsonTest\$ParentFieldBean.value)"
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")

    if result.returncode != 0:
        # Check that the failure is NOT about missing field info in error
        output = result.stdout + result.stderr
        # Look for the old error message format (without field names)
        old_pattern = r"Duplicate JSON field name detected while collecting field writers\s*$"
        if re.search(old_pattern, output, re.MULTILINE):
            assert False, (
                "Error message is missing field names. "
                "Expected format: 'Duplicate JSON field name...: FieldWriter(X) vs FieldWriter(Y)'"
            )

    assert result.returncode == 0, "Test should pass with improved error messages"


def test_field_writer_has_tostring():
    """Verify FieldWriter class has proper toString() method.

    The fix should add a toString() method to FieldWriter that returns
    the class name, declaring class, and field name.
    """
    instance_coercer_path = os.path.join(
        REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java"
    )

    with open(instance_coercer_path, 'r') as f:
        content = f.read()

    # Check that FieldWriter class exists with toString method
    assert "class FieldWriter" in content, "FieldWriter class should be defined"
    assert "public String toString()" in content, "FieldWriter should have toString() method"
    assert "field.getDeclaringClass().getName()" in content, (
        "toString should include declaring class name"
    )
    assert "field.getName()" in content, "toString should include field name"


def test_simple_property_writer_has_tostring():
    """Verify SimplePropertyWriter class has proper toString() method.

    The fix should add a toString() method to SimplePropertyWriter that
    includes the SimplePropertyDescriptor information.
    """
    instance_coercer_path = os.path.join(
        REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java"
    )

    with open(instance_coercer_path, 'r') as f:
        content = f.read()

    # Check that SimplePropertyWriter class exists with toString method
    assert "class SimplePropertyWriter" in content, (
        "SimplePropertyWriter class should be defined"
    )
    assert "public String toString()" in content, (
        "SimplePropertyWriter should have toString() method"
    )


def test_simple_property_descriptor_has_tostring():
    """Verify SimplePropertyDescriptor has proper toString() method.

    The fix should add a toString() method that returns "ClassName.fieldName".
    """
    descriptor_path = os.path.join(
        REPO, "java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java"
    )

    with open(descriptor_path, 'r') as f:
        content = f.read()

    # Check for toString method
    assert "public String toString()" in content, (
        "SimplePropertyDescriptor should have toString() method"
    )
    assert "clazz.getSimpleName()" in content, (
        "toString should include class simple name"
    )


def test_type_and_writer_returns_writer_tostring():
    """Verify TypeAndWriter.toString() delegates to writer.toString().

    This is essential for the error message to show field information.
    """
    instance_coercer_path = os.path.join(
        REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java"
    )

    with open(instance_coercer_path, 'r') as f:
        content = f.read()

    # Check that TypeAndWriter has toString that returns writer.toString()
    assert "return writer.toString()" in content, (
        "TypeAndWriter.toString() should return writer.toString()"
    )


def test_duplicate_field_merge_function_updated():
    """Verify the merge function in getFieldWriters includes field names in error.

    The old code threw an exception with a static message.
    The new code should format the message with existing and replacement info.
    """
    instance_coercer_path = os.path.join(
        REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java"
    )

    with open(instance_coercer_path, 'r') as f:
        content = f.read()

    # Check that the merge function includes %s vs %s format
    assert "%s vs %s" in content, (
        "Merge function should include field comparison format in error message"
    )


def test_bazel_build_java_src():
    """Pass-to-pass test: bazel build of java sources should succeed."""
    result = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/json:json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"Bazel build of java/src/org/openqa/selenium/json should succeed.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_bazel_build_json_tests():
    """Pass-to-pass test: bazel build of json test targets should succeed."""
    result = subprocess.run(
        ["bazel", "build", "//java/test/org/openqa/selenium/json:all"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"Bazel build of json tests should succeed.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_bazel_json_input_test():
    """Pass-to-pass test: JsonInputTest should pass (unit tests for JSON parsing)."""
    result = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/json:JsonInputTest",
         "--test_size_filters=small", "--test_output=errors"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"JsonInputTest should pass.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_bazel_json_output_test():
    """Pass-to-pass test: JsonOutputTest should pass (unit tests for JSON serialization)."""
    result = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/json:JsonOutputTest",
         "--test_size_filters=small", "--test_output=errors"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"JsonOutputTest should pass.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_bazel_query_json_targets():
    """Pass-to-pass test: bazel query for json targets should work."""
    result = subprocess.run(
        ["bazel", "query", "//java/test/org/openqa/selenium/json:all"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"Bazel query for json test targets should work.\n"
        f"STDERR: {result.stderr[-500:]}"
    )
    assert "JsonTest" in result.stdout, "Query should include JsonTest target"
    assert "JsonInputTest" in result.stdout, "Query should include JsonInputTest target"
    assert "JsonOutputTest" in result.stdout, "Query should include JsonOutputTest target"


def test_bazel_build_spotbugs():
    """Pass-to-pass test: bazel build of json spotbugs targets should succeed."""
    result = subprocess.run(
        ["bazel", "build", "//java/test/org/openqa/selenium/json:JsonTest-spotbugs"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"Bazel build of json spotbugs should succeed.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_bazel_smalltests_build():
    """Pass-to-pass test: bazel build of SmallTests aggregate target should succeed."""
    result = subprocess.run(
        ["bazel", "build", "//java/test/org/openqa/selenium/json:SmallTests"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"Bazel build of SmallTests should succeed.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )
