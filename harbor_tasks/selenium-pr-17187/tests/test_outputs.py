"""
Test suite for selenium-duplicate-field-json-exception task.

This task fixes InstanceCoercer#getFieldWriters to throw a descriptive JsonException
when duplicate field names are detected in a class hierarchy during JSON deserialization.
"""

import subprocess
import os
import re

REPO = "/workspace/selenium"


def test_fix_applied_in_source():
    """
    Verify the fix is applied: InstanceCoercer.getFieldWriters() includes a merge
    function that throws JsonException for duplicate field names (fail_to_pass).

    This test checks that the code contains the fix and compiles successfully.
    """
    file_path = os.path.join(REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java")

    with open(file_path, "r") as f:
        content = f.read()

    # Check that the merge function exists in the Collectors.toMap call
    # The fix adds a third argument to handle duplicate keys
    assert "Duplicate JSON field name detected while collecting field writers" in content, \
        "Fix not applied: Missing JsonException message for duplicate field detection"

    # Verify the code compiles
    result = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/json:json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Code with fix does not compile:\n{result.stderr[-2000:]}"


def test_merge_function_throws_json_exception():
    """
    Verify the merge function throws JsonException (not IllegalStateException) (fail_to_pass).

    The fix should throw JsonException, not let the collector throw IllegalStateException.
    """
    file_path = os.path.join(REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java")

    with open(file_path, "r") as f:
        content = f.read()

    # Find the getFieldWriters method and check for the merge function pattern
    # The fix adds: (existing, replacement) -> { throw new JsonException("..."); }

    # First verify the fix message exists
    assert "Duplicate JSON field name detected" in content, \
        "Fix not applied: Missing duplicate field detection message"

    # Check that it's throwing JsonException, not some other exception
    # The pattern should be: throw new JsonException followed by the message
    pattern = r'throw\s+new\s+JsonException\s*\(\s*"Duplicate JSON field name detected'
    assert re.search(pattern, content), \
        "Fix not properly implemented: Should throw JsonException with duplicate field message"


def test_getfieldwriters_has_merge_function():
    """
    Verify getFieldWriters uses Collectors.toMap with 3 arguments (fail_to_pass).

    Before fix: Collectors.toMap(keyMapper, valueMapper) - 2 args
    After fix: Collectors.toMap(keyMapper, valueMapper, mergeFunction) - 3 args
    """
    file_path = os.path.join(REPO, "java/src/org/openqa/selenium/json/InstanceCoercer.java")

    with open(file_path, "r") as f:
        content = f.read()

    # Find the getFieldWriters method
    # Look for the pattern where Collectors.toMap has a merge function
    # The merge function pattern is: (existing, replacement) ->

    assert "(existing, replacement) ->" in content, \
        "Fix not applied: Missing merge function in Collectors.toMap"


def test_json_library_builds():
    """
    Test that the JSON library builds successfully (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/json:json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-2000:]}"


def test_json_test_suite_passes():
    """
    Run the repo's JSON test suite to ensure no regressions (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/json:SmallTests",
         "--test_output=errors", "--test_timeout=300"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"JSON tests failed:\n{result.stderr[-2000:]}"


def test_core_small_tests_pass():
    """
    Run core selenium unit tests which use JSON serialization (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium:SmallTests",
         "--test_output=errors", "--test_timeout=300"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Core SmallTests failed:\n{result.stderr[-2000:]}"


def test_remote_small_tests_pass():
    """
    Run remote module tests which test JSON serialization/deserialization (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/remote:small-tests",
         "--test_output=errors", "--test_timeout=300"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Remote small-tests failed:\n{result.stderr[-2000:]}"
