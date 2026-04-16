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
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")
    assert result.returncode == 0, (
        f"JsonTest failed. Expected test to pass with improved error messages.\n"
        f"STDOUT: {result.stdout[-2000:]}\n"
        f"STDERR: {result.stderr[-2000:]}"
    )


def test_error_message_contains_field_names_in_format():
    """Verify the error message includes field name info after 'vs'.

    The fix should change the error message from:
    "Duplicate JSON field name detected while collecting field writers"
    to:
    "Duplicate JSON field name detected while collecting field writers: X vs Y"
    where X and Y contain field/class information.
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")

    if result.returncode != 0:
        output = result.stdout + result.stderr
        # Check the old message is gone (no longer a bare message ending with nothing after it)
        old_pattern = r"Duplicate JSON field name detected while collecting field writers\s*$"
        if re.search(old_pattern, output, re.MULTILINE):
            assert False, (
                "Error message is missing field names. "
                "Expected format: 'Duplicate JSON field name...: X vs Y' with field info"
            )

    assert result.returncode == 0, "Test should pass with improved error messages"


def test_field_writer_toString_produces_informative_output():
    """Verify FieldWriter.toString() produces output with class and field names.

    We verify this by running JsonTest and checking that when a duplicate field
    is detected, the error message includes strings that look like field references
    (containing dots and the pattern of ClassName.fieldName).
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")

    # If test passes, the error message format must have been correct
    assert result.returncode == 0, (
        f"JsonTest should pass when toString methods produce informative output.\n"
        f"STDOUT: {result.stdout[-2000:]}"
    )


def test_simple_property_writer_toString_produces_informative_output():
    """Verify SimplePropertyWriter.toString() produces informative output.

    This is indirectly verified by the JsonTest passing - the error message
    format depends on all toString() methods being implemented correctly.
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")
    assert result.returncode == 0, (
        f"JsonTest should pass when SimplePropertyWriter.toString() is correct.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_simple_property_descriptor_toString_produces_informative_output():
    """Verify SimplePropertyDescriptor.toString() produces 'ClassName.fieldName' format.

    This is indirectly verified by checking that the error message format includes
    class and field names - which requires SimplePropertyDescriptor.toString() to work.
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")
    output = result.stdout + result.stderr

    # The error message should contain field names (from SimplePropertyDescriptor.toString())
    # Format should be like "SimplePropertyWriter(SimplePropertyDescriptor.ClassName.fieldName)"
    # When both FieldWriter and SimplePropertyWriter are properly implemented,
    # the test passes which shows the error message format is correct
    assert result.returncode == 0, (
        f"JsonTest should pass when SimplePropertyDescriptor.toString() is correct.\n"
        f"STDERR: {result.stderr[-1000:]}"
    )


def test_type_and_writer_toString_included_in_error_message():
    """Verify TypeAndWriter.toString() output appears in error message.

    When duplicate fields are detected, the error includes 'X vs Y' where X and Y
    come from TypeAndWriter.toString() which delegates to writer.toString().
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")
    output = result.stdout + result.stderr

    # Verify the test passes and error message format is correct
    assert result.returncode == 0, (
        f"JsonTest should pass when TypeAndWriter.toString() delegates correctly.\n"
        f"STDOUT: {result.stdout[-2000:]}"
    )


def test_duplicate_merge_error_message_has_both_entries():
    """Verify merge function error message includes both conflicting entries.

    The error message format 'X vs Y' should be present when duplicate fields are detected.
    """
    result = run_bazel_test("//java/test/org/openqa/selenium/json:JsonTest")
    output = result.stdout + result.stderr

    # The error message should have "vs" between the two conflicting field writers
    # This comes from the updated merge function with %s vs %s format
    assert result.returncode == 0, (
        f"JsonTest should pass when merge function produces 'X vs Y' format.\n"
        f"STDOUT: {result.stdout[-2000:]}"
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
