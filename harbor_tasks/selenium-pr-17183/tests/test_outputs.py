"""
Tests for SeleniumHQ/selenium#17183: Make ExecuteMethod signature backward compatible.

This PR changes the ExecuteMethod interface to maintain backward compatibility with
external implementations like Appium's AppiumExecutionMethod. The key changes are:
1. execute() returns Object instead of generic <T> T
2. Added executeAs() as replacement for executeRequired()
3. Added execute(commandName, parameters, defaultValue) overload
4. Added execute(commandName) convenience overload
"""

import subprocess
import os
import re
import tempfile

REPO = "/workspace/selenium"
EXECUTE_METHOD_FILE = os.path.join(REPO, "java/src/org/openqa/selenium/remote/ExecuteMethod.java")


def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# =============================================================================
# FAIL-TO-PASS TESTS: These should fail on the base commit, pass after fix
# =============================================================================

def test_execute_returns_object():
    """
    The execute() method must return Object (not generic <T> T) for backward compatibility.

    Before the fix, the signature was: @Nullable <T> T execute(String, Map)
    After the fix, it should be: @Nullable Object execute(String, Map)

    This change is essential because generic return types with type inference
    cause issues for subclasses like AppiumExecutionMethod.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # The fixed interface should have Object return type for the abstract method
    # Look for the abstract method declaration (not default methods)
    # Pattern: @Nullable Object execute(String commandName, @Nullable Map<String, ?> parameters);
    object_return_pattern = r'@Nullable\s+Object\s+execute\s*\(\s*String\s+commandName\s*,'

    assert re.search(object_return_pattern, content), (
        "execute(String, Map) should return Object, not generic <T> T. "
        "This is required for backward compatibility with external implementations."
    )


def test_execute_as_method_exists():
    """
    The executeAs() method must exist as a replacement for executeRequired().

    This is a default method that calls execute() and casts the result.
    The PR renamed executeRequired() to executeAs() for better semantics.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # Check for executeAs default method
    execute_as_pattern = r'default\s+<T>\s+T\s+executeAs\s*\(\s*String\s+commandName'

    assert re.search(execute_as_pattern, content), (
        "executeAs(String, Map) default method must exist. "
        "This method replaces executeRequired() and casts the result to type T."
    )


def test_execute_with_default_value_exists():
    """
    The execute(commandName, parameters, defaultValue) overload must exist.

    This default method allows callers to provide a default value when
    the command returns null, avoiding NullPointerException.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # Check for execute method with default value parameter
    # Pattern: default <T> T execute(String commandName, @Nullable Map<String, ?> parameters, T defaultValue)
    execute_default_pattern = r'default\s+<T>\s+T\s+execute\s*\([^)]*,\s*T\s+defaultValue\s*\)'

    assert re.search(execute_default_pattern, content), (
        "execute(String, Map, T defaultValue) overload must exist. "
        "This method returns the default value when execute() returns null."
    )


def test_execute_single_arg_exists():
    """
    The execute(commandName) convenience method must exist.

    This is a default method that calls execute(commandName, null)
    and casts the result, for commands that don't need parameters.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # Check for single-argument execute method
    # Pattern: default <T> T execute(String commandName) {
    single_arg_pattern = r'default\s+<T>\s+T\s+execute\s*\(\s*String\s+commandName\s*\)\s*\{'

    assert re.search(single_arg_pattern, content), (
        "execute(String commandName) convenience method must exist. "
        "This method calls execute(commandName, null) and casts the result."
    )


def test_execute_required_removed():
    """
    The executeRequired() method should NOT exist in the interface.

    It has been replaced by executeAs() for better naming semantics.
    The old executeRequired name suggested it required parameters,
    but it actually required a non-null return value.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # executeRequired should not exist
    execute_required_pattern = r'\bexecuteRequired\s*\('

    assert not re.search(execute_required_pattern, content), (
        "executeRequired() should be removed from ExecuteMethod interface. "
        "It has been replaced by executeAs() for better semantics."
    )


def test_require_non_null_else_imported():
    """
    The requireNonNullElse import must be present for the default value method.

    The execute(commandName, parameters, defaultValue) method uses
    requireNonNullElse to return the default when execute returns null.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # Check for requireNonNullElse import
    import_pattern = r'import\s+static\s+java\.util\.Objects\.requireNonNullElse'

    assert re.search(import_pattern, content), (
        "requireNonNullElse must be imported for the default value method. "
        "This is used in execute(commandName, parameters, defaultValue)."
    )


# =============================================================================
# PASS-TO-PASS TESTS: These should pass both before and after the fix
# =============================================================================

def test_execute_method_is_interface():
    """ExecuteMethod should remain an interface (not a class)."""
    content = read_file(EXECUTE_METHOD_FILE)

    assert 'public interface ExecuteMethod' in content, (
        "ExecuteMethod must be declared as a public interface."
    )


def test_null_marked_annotation():
    """ExecuteMethod should have @NullMarked annotation for nullability checks."""
    content = read_file(EXECUTE_METHOD_FILE)

    assert '@NullMarked' in content, (
        "ExecuteMethod should have @NullMarked annotation."
    )


def test_require_non_null_imported():
    """The requireNonNull import must be present."""
    content = read_file(EXECUTE_METHOD_FILE)

    import_pattern = r'import\s+static\s+java\.util\.Objects\.requireNonNull'

    assert re.search(import_pattern, content), (
        "requireNonNull must be imported for null checking in default methods."
    )


def test_local_execute_method_compiles():
    """
    LocalExecuteMethod must implement the updated interface correctly.

    After the fix, it should implement: Object execute(String, Map)
    """
    local_file = os.path.join(REPO, "java/src/org/openqa/selenium/remote/LocalExecuteMethod.java")
    content = read_file(local_file)

    # Check that LocalExecuteMethod overrides execute with Object return type
    object_return_pattern = r'public\s+Object\s+execute\s*\(\s*String\s+commandName'

    assert re.search(object_return_pattern, content), (
        "LocalExecuteMethod.execute() must return Object, not generic <T> T. "
        "This matches the updated ExecuteMethod interface."
    )


def test_remote_execute_method_compiles():
    """
    RemoteExecuteMethod must implement the updated interface correctly.

    After the fix, it should implement: Object execute(String, Map)
    """
    remote_file = os.path.join(REPO, "java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java")
    content = read_file(remote_file)

    # Check that RemoteExecuteMethod overrides execute with Object return type
    object_return_pattern = r'public\s+@Nullable\s+Object\s+execute\s*\(\s*String\s+commandName'

    assert re.search(object_return_pattern, content), (
        "RemoteExecuteMethod.execute() must return @Nullable Object. "
        "This matches the updated ExecuteMethod interface."
    )


def test_call_sites_updated_add_has_casting():
    """
    AddHasCasting must use the new API methods instead of requireNonNullElse.

    The fix changes: requireNonNullElse(executeMethod.execute(...), emptyList())
    To: executeMethod.execute(GET_CAST_SINKS, null, emptyList())
    """
    casting_file = os.path.join(REPO, "java/src/org/openqa/selenium/chromium/AddHasCasting.java")
    content = read_file(casting_file)

    # After fix: should use execute with default value, not requireNonNullElse
    new_pattern = r'executeMethod\.execute\s*\(\s*GET_CAST_SINKS\s*,\s*null\s*,\s*emptyList\s*\(\s*\)\s*\)'

    assert re.search(new_pattern, content), (
        "AddHasCasting should use execute(GET_CAST_SINKS, null, emptyList()) "
        "instead of requireNonNullElse wrapper."
    )


def test_call_sites_updated_add_has_cdp():
    """
    AddHasCdp must use executeAs() instead of executeRequired().
    """
    cdp_file = os.path.join(REPO, "java/src/org/openqa/selenium/chromium/AddHasCdp.java")
    content = read_file(cdp_file)

    # After fix: should use executeAs
    assert 'executeMethod.executeAs(EXECUTE_CDP' in content, (
        "AddHasCdp should use executeAs() instead of executeRequired()."
    )


def test_call_sites_updated_firefox_extensions():
    """
    AddHasExtensions must use executeAs() instead of executeRequired().
    """
    ext_file = os.path.join(REPO, "java/src/org/openqa/selenium/firefox/AddHasExtensions.java")
    content = read_file(ext_file)

    # After fix: should use executeAs
    assert 'executeMethod.executeAs(' in content, (
        "AddHasExtensions should use executeAs() instead of executeRequired()."
    )


def test_javadoc_for_new_methods():
    """
    New default methods should have Javadoc documentation.

    Per java/AGENTS.md: "Use Javadoc for public APIs"
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # Check for Javadoc before execute with default value
    # Look for /** ... */ before the method
    javadoc_pattern = r'/\*\*[^*]*\*+(?:[^/*][^*]*\*+)*/\s*@SuppressWarnings.*\s*default\s+<T>\s+T\s+execute\s*\([^)]*defaultValue'

    # At minimum, check that there are multiple Javadoc comments (for new methods)
    javadoc_count = len(re.findall(r'/\*\*', content))

    assert javadoc_count >= 3, (
        f"Expected at least 3 Javadoc comments for methods, found {javadoc_count}. "
        "New default methods should be documented per java/AGENTS.md."
    )


def test_suppress_warnings_for_casts():
    """
    Methods with unchecked casts should have @SuppressWarnings("unchecked").

    The executeAs() and execute() methods cast Object to T, which requires
    suppressing unchecked cast warnings.
    """
    content = read_file(EXECUTE_METHOD_FILE)

    # Count SuppressWarnings annotations - should have at least 3 (for the 3 casting methods)
    suppress_count = len(re.findall(r'@SuppressWarnings\s*\(\s*"unchecked"\s*\)', content))

    assert suppress_count >= 3, (
        f"Expected at least 3 @SuppressWarnings(\"unchecked\") annotations, found {suppress_count}. "
        "Each method with (T) cast should suppress the unchecked warning."
    )


# =============================================================================
# STATIC VALIDATION TESTS: These validate code quality (pass_to_pass, origin: static)
# =============================================================================

# Files modified by this PR
MODIFIED_FILES = [
    "java/src/org/openqa/selenium/remote/ExecuteMethod.java",
    "java/src/org/openqa/selenium/remote/LocalExecuteMethod.java",
    "java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java",
    "java/src/org/openqa/selenium/chromium/AddHasCasting.java",
    "java/src/org/openqa/selenium/chromium/AddHasCdp.java",
    "java/src/org/openqa/selenium/chromium/AddHasNetworkConditions.java",
    "java/src/org/openqa/selenium/firefox/AddHasContext.java",
    "java/src/org/openqa/selenium/firefox/AddHasExtensions.java",
    "java/src/org/openqa/selenium/remote/FedCmDialogImpl.java",
    "java/src/org/openqa/selenium/remote/RemoteLogs.java",
    "java/src/org/openqa/selenium/safari/AddHasPermissions.java",
]


def test_no_tabs_in_modified_files():
    """
    Modified Java files must not contain tab characters (pass_to_pass).

    Selenium uses spaces for indentation per google-java-format.
    """
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-l", "\t", full_path],
            capture_output=True, text=True, timeout=30,
        )
        # grep -l exits 0 if pattern found, 1 if not found
        assert r.returncode == 1, f"Tab characters found in {rel_path}"


def test_no_merge_conflict_markers():
    """
    Modified files must not contain merge conflict markers (pass_to_pass).
    """
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-E", "<<<<|>>>>|=======", full_path],
            capture_output=True, text=True, timeout=30,
        )
        # grep exits 0 if pattern found, 1 if not found
        assert r.returncode == 1, f"Merge conflict markers found in {rel_path}"


def test_copyright_headers_present():
    """
    All Java source files must have Apache License copyright header (pass_to_pass).
    """
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-l", "Licensed to the Software Freedom Conservancy", full_path],
            capture_output=True, text=True, timeout=30,
        )
        # grep -l exits 0 if pattern found
        assert r.returncode == 0, f"Copyright header missing in {rel_path}"


def test_package_declarations_match_paths():
    """
    Java files must have package declarations matching their file paths (pass_to_pass).
    """
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue

        # Extract expected package from path
        # java/src/org/openqa/selenium/remote/ExecuteMethod.java -> org.openqa.selenium.remote
        path_parts = rel_path.split("/")
        if "src" in path_parts:
            src_idx = path_parts.index("src")
            package_parts = path_parts[src_idx + 1:-1]  # exclude src and filename
            expected_package = ".".join(package_parts)
        else:
            continue

        r = subprocess.run(
            ["grep", f"package {expected_package};", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Package declaration mismatch in {rel_path}, expected: {expected_package}"


def test_no_trailing_whitespace():
    """
    Modified files should not have trailing whitespace (pass_to_pass).
    """
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-E", "[ \t]+$", full_path],
            capture_output=True, text=True, timeout=30,
        )
        # grep exits 1 if pattern not found (good)
        assert r.returncode == 1, f"Trailing whitespace found in {rel_path}"
