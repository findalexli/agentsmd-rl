"""
Tests for Selenium Lazy class RuntimeException handling fix.

PR: SeleniumHQ/selenium#17233
Bug: RuntimeException thrown by supplier was being wrapped in InitializationException
Fix: Re-throw RuntimeException directly, only wrap checked exceptions
"""

import subprocess
import os
import tempfile
import shutil

REPO = "/workspace/selenium"


def compile_java_test(test_code: str, test_name: str) -> str:
    """Compile a Java test file that imports and tests the Lazy class.

    Returns the path to the compiled test directory.
    """
    # Create temp directory for compilation
    temp_dir = tempfile.mkdtemp()

    # Copy the Lazy.java source to temp location
    lazy_src = os.path.join(REPO, "java/src/org/openqa/selenium/concurrent/Lazy.java")
    concurrent_dir = os.path.join(temp_dir, "org/openqa/selenium/concurrent")
    os.makedirs(concurrent_dir, exist_ok=True)

    # Read and modify Lazy.java to remove jspecify annotation (not needed for test)
    with open(lazy_src, 'r') as f:
        lazy_content = f.read()
    lazy_content = lazy_content.replace("import org.jspecify.annotations.Nullable;", "")
    lazy_content = lazy_content.replace("@Nullable ", "")

    with open(os.path.join(concurrent_dir, "Lazy.java"), 'w') as f:
        f.write(lazy_content)

    # Write test file
    with open(os.path.join(temp_dir, f"{test_name}.java"), 'w') as f:
        f.write(test_code)

    # Compile Lazy.java first
    result = subprocess.run(
        ["javac", os.path.join(concurrent_dir, "Lazy.java")],
        capture_output=True,
        text=True,
        cwd=temp_dir,
        timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to compile Lazy.java: {result.stderr}")

    # Compile test file
    result = subprocess.run(
        ["javac", "-cp", temp_dir, f"{test_name}.java"],
        capture_output=True,
        text=True,
        cwd=temp_dir,
        timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to compile test: {result.stderr}")

    return temp_dir


def run_java_test(test_dir: str, test_name: str) -> subprocess.CompletedProcess:
    """Run a compiled Java test class and return the result."""
    return subprocess.run(
        ["java", "-cp", test_dir, test_name],
        capture_output=True,
        text=True,
        cwd=test_dir,
        timeout=30
    )


def test_runtime_exception_not_wrapped():
    """RuntimeException thrown by supplier should NOT be wrapped in InitializationException.

    This is a fail_to_pass test - it fails on base commit, passes after fix.
    """
    test_code = '''
import org.openqa.selenium.concurrent.Lazy;

public class TestRuntimeExceptionNotWrapped {
    public static void main(String[] args) {
        // Create a Lazy that throws IllegalStateException (a RuntimeException)
        Lazy<String> lazy = Lazy.lazy(() -> {
            throw new IllegalStateException("test runtime exception");
        });

        try {
            lazy.get();
            System.out.println("FAIL: No exception was thrown");
            System.exit(1);
        } catch (IllegalStateException e) {
            // SUCCESS: The original RuntimeException was thrown directly
            if ("test runtime exception".equals(e.getMessage())) {
                System.out.println("PASS: RuntimeException thrown directly without wrapping");
                System.exit(0);
            } else {
                System.out.println("FAIL: Wrong message: " + e.getMessage());
                System.exit(1);
            }
        } catch (Lazy.InitializationException e) {
            // FAIL: The exception was wrapped (this is the bug!)
            System.out.println("FAIL: RuntimeException was wrapped in InitializationException");
            System.exit(1);
        } catch (Throwable e) {
            System.out.println("FAIL: Unexpected exception type: " + e.getClass().getName());
            System.exit(1);
        }
    }
}
'''
    test_dir = compile_java_test(test_code, "TestRuntimeExceptionNotWrapped")
    try:
        result = run_java_test(test_dir, "TestRuntimeExceptionNotWrapped")
        assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_runtime_exception_various_types():
    """Various RuntimeException subtypes should all pass through unwrapped.

    This is a fail_to_pass test using multiple RuntimeException types.
    """
    test_code = '''
import org.openqa.selenium.concurrent.Lazy;

public class TestRuntimeExceptionTypes {
    public static void main(String[] args) {
        // Test IllegalArgumentException
        testException(new IllegalArgumentException("arg error"), "IllegalArgumentException");

        // Test NullPointerException
        testException(new NullPointerException("null error"), "NullPointerException");

        // Test UnsupportedOperationException
        testException(new UnsupportedOperationException("unsupported"), "UnsupportedOperationException");

        System.out.println("PASS: All RuntimeException types passed through correctly");
        System.exit(0);
    }

    static void testException(RuntimeException toThrow, String name) {
        Lazy<String> lazy = Lazy.lazy(() -> { throw toThrow; });

        try {
            lazy.get();
            System.out.println("FAIL: No exception thrown for " + name);
            System.exit(1);
        } catch (Lazy.InitializationException e) {
            System.out.println("FAIL: " + name + " was wrapped in InitializationException");
            System.exit(1);
        } catch (RuntimeException e) {
            if (e != toThrow) {
                System.out.println("FAIL: Wrong exception instance for " + name);
                System.exit(1);
            }
            // Success for this type
        }
    }
}
'''
    test_dir = compile_java_test(test_code, "TestRuntimeExceptionTypes")
    try:
        result = run_java_test(test_dir, "TestRuntimeExceptionTypes")
        assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_checked_exception_still_wrapped():
    """Checked exceptions should still be wrapped in InitializationException.

    This is a pass_to_pass test - ensures fix doesn't break existing behavior.
    """
    test_code = '''
import org.openqa.selenium.concurrent.Lazy;
import java.io.IOException;

public class TestCheckedExceptionWrapped {
    public static void main(String[] args) {
        // Create a Lazy that throws IOException (a checked exception)
        Lazy<String> lazy = Lazy.lazy(() -> {
            throw new IOException("test checked exception");
        });

        try {
            lazy.get();
            System.out.println("FAIL: No exception was thrown");
            System.exit(1);
        } catch (Lazy.InitializationException e) {
            // SUCCESS: Checked exception should be wrapped
            if (e.getCause() instanceof IOException) {
                System.out.println("PASS: Checked exception correctly wrapped in InitializationException");
                System.exit(0);
            } else {
                System.out.println("FAIL: Wrong cause type: " + e.getCause().getClass().getName());
                System.exit(1);
            }
        } catch (Throwable e) {
            System.out.println("FAIL: Unexpected exception type: " + e.getClass().getName());
            System.exit(1);
        }
    }
}
'''
    test_dir = compile_java_test(test_code, "TestCheckedExceptionWrapped")
    try:
        result = run_java_test(test_dir, "TestCheckedExceptionWrapped")
        assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_lazy_normal_operation():
    """Lazy should work normally when supplier succeeds.

    This is a pass_to_pass test - basic functionality check.
    """
    test_code = '''
import org.openqa.selenium.concurrent.Lazy;

public class TestLazyNormalOperation {
    public static void main(String[] args) {
        // Test normal value retrieval
        Lazy<String> lazy = Lazy.lazy(() -> "hello world");

        String result = lazy.get();
        if (!"hello world".equals(result)) {
            System.out.println("FAIL: Wrong value returned: " + result);
            System.exit(1);
        }

        // Test that value is cached (same instance returned)
        String result2 = lazy.get();
        if (result != result2) {
            System.out.println("FAIL: Value not cached properly");
            System.exit(1);
        }

        // Test getIfInitialized returns value after get()
        if (!lazy.getIfInitialized().isPresent()) {
            System.out.println("FAIL: getIfInitialized should return value after get()");
            System.exit(1);
        }

        System.out.println("PASS: Lazy normal operation works correctly");
        System.exit(0);
    }
}
'''
    test_dir = compile_java_test(test_code, "TestLazyNormalOperation")
    try:
        result = run_java_test(test_dir, "TestLazyNormalOperation")
        assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_lazy_source_compiles():
    """The Lazy.java source file should compile without errors.

    This is a pass_to_pass test - ensures source file is valid Java.
    """
    lazy_src = os.path.join(REPO, "java/src/org/openqa/selenium/concurrent/Lazy.java")
    temp_dir = tempfile.mkdtemp()

    try:
        # Copy and modify the source
        concurrent_dir = os.path.join(temp_dir, "org/openqa/selenium/concurrent")
        os.makedirs(concurrent_dir, exist_ok=True)

        with open(lazy_src, 'r') as f:
            content = f.read()
        content = content.replace("import org.jspecify.annotations.Nullable;", "")
        content = content.replace("@Nullable ", "")

        with open(os.path.join(concurrent_dir, "Lazy.java"), 'w') as f:
            f.write(content)

        result = subprocess.run(
            ["javac", os.path.join(concurrent_dir, "Lazy.java")],
            capture_output=True,
            text=True,
            cwd=temp_dir,
            timeout=60
        )
        assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_concurrent_package_compiles():
    """All Java files in concurrent package compile together without errors.

    This is a pass_to_pass test - verifies changes to Lazy.java don't break
    package-level compilation with ExecutorServices.java and GuardedRunnable.java.
    """
    concurrent_src_dir = os.path.join(REPO, "java/src/org/openqa/selenium/concurrent")
    temp_dir = tempfile.mkdtemp()

    try:
        # Create package directory structure
        concurrent_dir = os.path.join(temp_dir, "org/openqa/selenium/concurrent")
        os.makedirs(concurrent_dir, exist_ok=True)

        # Files to compile (excluding package-info.java which has special annotation needs)
        java_files = ["Lazy.java", "ExecutorServices.java", "GuardedRunnable.java"]

        for java_file in java_files:
            src_path = os.path.join(concurrent_src_dir, java_file)
            if os.path.exists(src_path):
                with open(src_path, 'r') as f:
                    content = f.read()
                # Remove jspecify annotations which require external dependency
                content = content.replace("import org.jspecify.annotations.Nullable;", "")
                content = content.replace("@Nullable ", "")
                with open(os.path.join(concurrent_dir, java_file), 'w') as f:
                    f.write(content)

        # Compile all files together
        result = subprocess.run(
            ["javac"] + [os.path.join(concurrent_dir, f) for f in java_files],
            capture_output=True,
            text=True,
            cwd=temp_dir,
            timeout=120
        )
        assert result.returncode == 0, f"Package compilation failed:\n{result.stderr}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_git_repo_valid():
    """Git repository is in a valid state after applying patch.

    This is a pass_to_pass test - verifies git operations work correctly.
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30
    )
    assert result.returncode == 0, f"Git repo invalid:\n{result.stderr}"
    # Verify we got a valid commit hash (40 hex chars)
    commit_hash = result.stdout.strip()
    assert len(commit_hash) == 40, f"Invalid commit hash: {commit_hash}"
    assert all(c in '0123456789abcdef' for c in commit_hash), f"Invalid commit hash: {commit_hash}"


def test_lazy_java_file_parseable():
    """Lazy.java is valid UTF-8 and has proper Java structure.

    This is a pass_to_pass test - verifies file integrity.
    """
    lazy_path = os.path.join(REPO, "java/src/org/openqa/selenium/concurrent/Lazy.java")

    # Read as UTF-8 (will fail if encoding is wrong)
    with open(lazy_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic Java structure validation
    assert "package org.openqa.selenium.concurrent;" in content, "Missing package declaration"
    assert "public final class Lazy<T>" in content, "Missing class declaration"
    assert "public T get()" in content, "Missing get() method"
    assert "public static <T> Lazy<T> lazy(" in content, "Missing lazy() factory method"
