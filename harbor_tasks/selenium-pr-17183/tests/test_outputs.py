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
import shutil
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

def test_interface_compiles_and_default_methods_work():
    """
    Compile ExecuteMethod.java and verify the interface methods exist with
    correct signatures and default methods produce correct runtime behavior.

    This is a behavioral test: it compiles the actual interface, creates a
    real implementation, and executes it to verify:
    - execute() returns Object (not generic <T>)
    - executeAs() exists and casts + enforces non-null
    - execute(cmd, params, defaultValue) returns default when null
    - execute(cmd) single-arg convenience works
    - executeRequired() does NOT exist
    """
    tmpdir = tempfile.mkdtemp()
    try:
        # Create stub annotation files for jspecify (not on classpath)
        annot_dir = os.path.join(tmpdir, "org", "jspecify", "annotations")
        os.makedirs(annot_dir, exist_ok=True)

        with open(os.path.join(annot_dir, "NullMarked.java"), 'w') as f:
            f.write(
                "package org.jspecify.annotations;\n"
                "import java.lang.annotation.*;\n"
                "@Retention(RetentionPolicy.RUNTIME)\n"
                "@Target({ElementType.TYPE, ElementType.PACKAGE})\n"
                "public @interface NullMarked {}\n"
            )

        with open(os.path.join(annot_dir, "Nullable.java"), 'w') as f:
            f.write(
                "package org.jspecify.annotations;\n"
                "import java.lang.annotation.*;\n"
                "@Retention(RetentionPolicy.RUNTIME)\n"
                "@Target({ElementType.TYPE_USE})\n"
                "public @interface Nullable {}\n"
            )

        # Copy the actual ExecuteMethod.java
        em_dest_dir = os.path.join(tmpdir, "org", "openqa", "selenium", "remote")
        os.makedirs(em_dest_dir, exist_ok=True)
        shutil.copy2(EXECUTE_METHOD_FILE, em_dest_dir)

        # Write a test program that exercises the interface behaviorally
        test_java = os.path.join(tmpdir, "TestExecuteMethod.java")
        with open(test_java, 'w') as f:
            f.write(
                'import org.openqa.selenium.remote.ExecuteMethod;\n'
                'import java.util.Map;\n'
                '\n'
                'public class TestExecuteMethod {\n'
                '    public static void main(String[] args) throws Exception {\n'
                '        // Implement the interface - abstract method must return Object\n'
                '        ExecuteMethod em = new ExecuteMethod() {\n'
                '            @Override\n'
                '            public Object execute(String cmd, Map<String, ?> params) {\n'
                '                if ("null_cmd".equals(cmd)) return null;\n'
                '                return "result_" + cmd;\n'
                '            }\n'
                '        };\n'
                '\n'
                '        // Test 1: execute returns Object\n'
                '        Object r1 = em.execute("test", null);\n'
                '        assert "result_test".equals(r1) : "execute should return Object";\n'
                '\n'
                '        // Test 2: executeAs casts result and enforces non-null\n'
                '        String r2 = em.executeAs("test", null);\n'
                '        assert "result_test".equals(r2) : "executeAs should cast";\n'
                '\n'
                '        // Test 3: execute with defaultValue returns default for null\n'
                '        String r3 = em.execute("null_cmd", null, "fallback");\n'
                '        assert "fallback".equals(r3) : "should return default";\n'
                '\n'
                '        // Test 4: single-arg execute works\n'
                '        String r4 = em.execute("test");\n'
                '        assert "result_test".equals(r4) : "single arg should work";\n'
                '\n'
                '        // Test 5: executeRequired must NOT exist\n'
                '        try {\n'
                '            ExecuteMethod.class.getMethod("executeRequired",\n'
                '                String.class, Map.class);\n'
                '            throw new AssertionError("executeRequired should not exist");\n'
                '        } catch (NoSuchMethodException e) { /* expected */ }\n'
                '\n'
                '        System.out.println("ALL_BEHAVIORAL_TESTS_PASSED");\n'
                '    }\n'
                '}\n'
            )

        # Find all Java source files to compile
        java_files = [
            os.path.join(annot_dir, "NullMarked.java"),
            os.path.join(annot_dir, "Nullable.java"),
            os.path.join(em_dest_dir, "ExecuteMethod.java"),
            test_java,
        ]

        # Compile
        r = subprocess.run(
            ["javac"] + java_files,
            capture_output=True, text=True, timeout=60, cwd=tmpdir,
        )
        assert r.returncode == 0, f"Compilation failed:\n{r.stderr}"

        # Run
        r = subprocess.run(
            ["java", "-ea", "-cp", tmpdir, "TestExecuteMethod"],
            capture_output=True, text=True, timeout=30, cwd=tmpdir,
        )
        assert r.returncode == 0, f"Execution failed:\n{r.stderr}"
        assert "ALL_BEHAVIORAL_TESTS_PASSED" in r.stdout, (
            f"Behavioral tests did not pass. stdout: {r.stdout}"
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_execute_returns_object():
    """
    The execute() method must return Object (not generic <T> T) for backward compatibility.
    """
    content = read_file(EXECUTE_METHOD_FILE)
    object_return_pattern = r'@Nullable\s+Object\s+execute\s*\(\s*String\s+commandName\s*,'
    assert re.search(object_return_pattern, content), (
        "execute(String, Map) should return Object, not generic <T> T."
    )


def test_execute_required_removed():
    """
    The executeRequired() method should NOT exist in the interface.
    It has been replaced by executeAs().
    """
    content = read_file(EXECUTE_METHOD_FILE)
    assert not re.search(r'\bexecuteRequired\s*\(', content), (
        "executeRequired() should be removed from ExecuteMethod interface."
    )


def test_require_non_null_else_imported():
    """
    The requireNonNullElse import must be present for the default value method.
    """
    content = read_file(EXECUTE_METHOD_FILE)
    import_pattern = r'import\s+static\s+java\.util\.Objects\.requireNonNullElse'
    assert re.search(import_pattern, content), (
        "requireNonNullElse must be imported for the default value method."
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

    object_return_pattern = r'public\s+Object\s+execute\s*\(\s*String\s+commandName'

    assert re.search(object_return_pattern, content), (
        "LocalExecuteMethod.execute() must return Object, not generic <T> T."
    )


def test_remote_execute_method_compiles():
    """
    RemoteExecuteMethod must implement the updated interface correctly.
    After the fix, it should implement: Object execute(String, Map)
    """
    remote_file = os.path.join(REPO, "java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java")
    content = read_file(remote_file)

    object_return_pattern = r'public\s+@Nullable\s+Object\s+execute\s*\(\s*String\s+commandName'

    assert re.search(object_return_pattern, content), (
        "RemoteExecuteMethod.execute() must return @Nullable Object."
    )


def test_call_sites_updated_add_has_casting():
    """
    AddHasCasting must use the new execute(cmd, params, defaultValue) overload.
    """
    casting_file = os.path.join(REPO, "java/src/org/openqa/selenium/chromium/AddHasCasting.java")
    content = read_file(casting_file)

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

    assert 'executeMethod.executeAs(EXECUTE_CDP' in content, (
        "AddHasCdp should use executeAs() instead of executeRequired()."
    )


def test_call_sites_updated_firefox_extensions():
    """
    AddHasExtensions must use executeAs() instead of executeRequired().
    """
    ext_file = os.path.join(REPO, "java/src/org/openqa/selenium/firefox/AddHasExtensions.java")
    content = read_file(ext_file)

    assert 'executeMethod.executeAs(' in content, (
        "AddHasExtensions should use executeAs() instead of executeRequired()."
    )


def test_javadoc_for_new_methods():
    """
    New default methods should have Javadoc documentation.
    Per java/AGENTS.md: "Use Javadoc for public APIs"
    """
    content = read_file(EXECUTE_METHOD_FILE)

    javadoc_count = len(re.findall(r'/\*\*', content))

    assert javadoc_count >= 3, (
        f"Expected at least 3 Javadoc comments for methods, found {javadoc_count}. "
        "New default methods should be documented per java/AGENTS.md."
    )


def test_suppress_warnings_for_casts():
    """
    Methods with unchecked casts should have @SuppressWarnings("unchecked").
    """
    content = read_file(EXECUTE_METHOD_FILE)

    suppress_count = len(re.findall(r'@SuppressWarnings\s*\(\s*"unchecked"\s*\)', content))

    assert suppress_count >= 3, (
        f"Expected at least 3 @SuppressWarnings(\"unchecked\") annotations, found {suppress_count}."
    )


# =============================================================================
# STATIC VALIDATION TESTS: These validate code quality (pass_to_pass, origin: static)
# =============================================================================

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
    """Modified Java files must not contain tab characters (pass_to_pass)."""
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-l", "\t", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 1, f"Tab characters found in {rel_path}"


def test_no_merge_conflict_markers():
    """Modified files must not contain merge conflict markers (pass_to_pass)."""
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-E", "<<<<|>>>>|=======", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 1, f"Merge conflict markers found in {rel_path}"


def test_copyright_headers_present():
    """All Java source files must have Apache License copyright header (pass_to_pass)."""
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-l", "Licensed to the Software Freedom Conservancy", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Copyright header missing in {rel_path}"


def test_package_declarations_match_paths():
    """Java files must have package declarations matching their file paths (pass_to_pass)."""
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue

        path_parts = rel_path.split("/")
        if "src" in path_parts:
            src_idx = path_parts.index("src")
            package_parts = path_parts[src_idx + 1:-1]
            expected_package = ".".join(package_parts)
        else:
            continue

        r = subprocess.run(
            ["grep", f"package {expected_package};", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Package declaration mismatch in {rel_path}, expected: {expected_package}"


def test_no_trailing_whitespace():
    """Modified files should not have trailing whitespace (pass_to_pass)."""
    for rel_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            continue
        r = subprocess.run(
            ["grep", "-E", "[ \t]+$", full_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 1, f"Trailing whitespace found in {rel_path}"
