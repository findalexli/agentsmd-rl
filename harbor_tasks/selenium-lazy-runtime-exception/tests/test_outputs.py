#!/usr/bin/env python3
"""Tests for Selenium Lazy.java exception handling fix."""

import subprocess
import os
import sys
import shutil

REPO = "/workspace/selenium"


def _get_bazel_jar():
    """Get the Bazel jar path dynamically."""
    # Get bazel output directory
    result = subprocess.run(
        ["bazel", "info", "bazel-bin"],
        capture_output=True, text=True, cwd=REPO, timeout=60
    )
    if result.returncode != 0:
        # Fallback to default path
        return "/workspace/selenium/bazel-bin/java/src/org/openqa/selenium/concurrent/libconcurrent.jar"
    bazel_bin = result.stdout.strip()
    return f"{bazel_bin}/java/src/org/openqa/selenium/concurrent/libconcurrent.jar"


BAZEL_JAR = None  # Will be set by _ensure_bazel_build()

def _ensure_bazel_build():
    """Ensure the concurrent jar is built with latest source."""
    global BAZEL_JAR
    BAZEL_JAR = _get_bazel_jar()

    # Always rebuild to ensure we're testing the current state of Lazy.java
    # This handles both fresh builds and when source was modified after initial build
    lazy_source = os.path.join(REPO, "java/src/org/openqa/selenium/concurrent/Lazy.java")
    lazy_mtime = os.path.getmtime(lazy_source) if os.path.exists(lazy_source) else 0
    jar_mtime = os.path.getmtime(BAZEL_JAR) if os.path.exists(BAZEL_JAR) else 0

    if not os.path.exists(BAZEL_JAR) or lazy_mtime > jar_mtime:
        cmd = ["bazel", "build", "//java/src/org/openqa/selenium/concurrent:concurrent"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=REPO)
        if result.returncode != 0:
            raise AssertionError(f"Bazel build failed: {result.stderr[-500:]}")


def _create_test_java_file(test_dir, class_name, content):
    """Helper to create a Java test file."""
    os.makedirs(test_dir, exist_ok=True)
    test_file = os.path.join(test_dir, f"{class_name}.java")
    with open(test_file, "w") as f:
        f.write(content)
    return test_file


def _compile_test(test_dir, test_java_file):
    """Compile a test file against the bazel-built jar."""
    cmd = [
        "javac", "-cp", BAZEL_JAR,
        "-d", test_dir,
        test_java_file,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result


def test_runtime_exception_not_wrapped():
    """
    RuntimeException thrown by the supplier should NOT be wrapped in InitializationException.
    This is the main fail-to_pass test.
    """
    _ensure_bazel_build()

    test_code = '''
import org.openqa.selenium.concurrent.Lazy;

public class TestRuntimeException {
    public static void main(String[] args) {
        Lazy<String> lazy = Lazy.lazy(() -> {
            throw new IllegalStateException("test runtime exception");
        });
        try {
            lazy.get();
            System.out.println("FAIL: Expected exception was not thrown");
            System.exit(1);
        } catch (IllegalStateException e) {
            if (e.getMessage().equals("test runtime exception")) {
                System.out.println("PASS: RuntimeException preserved");
                System.exit(0);
            } else {
                System.out.println("FAIL: Wrong message: " + e.getMessage());
                System.exit(1);
            }
        } catch (Exception e) {
            System.out.println("FAIL: RuntimeException was wrapped in: " + e.getClass().getName());
            System.out.println("Cause: " + e.getCause());
            System.exit(1);
        }
    }
}
'''

    test_dir = os.path.join(REPO, "test_output_dir")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    test_file = _create_test_java_file(test_dir, "TestRuntimeException", test_code)

    result = _compile_test(test_dir, test_file)
    if result.returncode != 0:
        raise AssertionError(f"Compilation failed: {result.stderr}")

    cmd = ["java", "-cp", f"{test_dir}:{BAZEL_JAR}", "TestRuntimeException"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if "PASS: RuntimeException preserved" not in result.stdout:
        raise AssertionError(f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}")


def test_various_runtime_exceptions():
    """
    Test with various RuntimeException subclasses: IllegalArgument, NullPointer, etc.
    """
    _ensure_bazel_build()

    test_code = '''
import org.openqa.selenium.concurrent.Lazy;

public class TestVariousRuntimeExceptions {
    static int testCount = 0;
    static int passCount = 0;

    static void testException(String exName, String message, ExceptionThrower thrower) {
        testCount++;
        Lazy<String> lazy = Lazy.lazy(() -> {
            throw thrower.throwException();
        });
        try {
            lazy.get();
            System.out.println("FAIL: " + exName + " not thrown");
        } catch (IllegalArgumentException e) {
            if (exName.equals("IllegalArgumentException") && e.getMessage().equals(message)) {
                System.out.println("PASS: " + exName + " preserved");
                passCount++;
            } else {
                System.out.println("FAIL: " + exName + " got IllegalArgumentException");
            }
        } catch (NullPointerException e) {
            if (exName.equals("NullPointerException") && e.getMessage().equals(message)) {
                System.out.println("PASS: " + exName + " preserved");
                passCount++;
            } else {
                System.out.println("FAIL: " + exName + " got NullPointerException");
            }
        } catch (IllegalStateException e) {
            if (exName.equals("IllegalStateException") && e.getMessage().equals(message)) {
                System.out.println("PASS: " + exName + " preserved");
                passCount++;
            } else {
                System.out.println("FAIL: " + exName + " got IllegalStateException");
            }
        } catch (UnsupportedOperationException e) {
            if (exName.equals("UnsupportedOperationException") && e.getMessage().equals(message)) {
                System.out.println("PASS: " + exName + " preserved");
                passCount++;
            } else {
                System.out.println("FAIL: " + exName + " got UnsupportedOperationException");
            }
        } catch (Exception e) {
            System.out.println("FAIL: " + exName + " wrapped in " + e.getClass().getSimpleName());
        }
    }

    @FunctionalInterface
    interface ExceptionThrower {
        RuntimeException throwException();
    }

    public static void main(String[] args) {
        testException("IllegalArgumentException", "illegal arg", () -> new IllegalArgumentException("illegal arg"));
        testException("NullPointerException", "null ptr", () -> new NullPointerException("null ptr"));
        testException("IllegalStateException", "illegal state", () -> new IllegalStateException("illegal state"));
        testException("UnsupportedOperationException", "unsupported", () -> new UnsupportedOperationException("unsupported"));

        System.out.println("Results: " + passCount + "/" + testCount);
        if (passCount == testCount) {
            System.exit(0);
        } else {
            System.exit(1);
        }
    }
}
'''

    test_dir = os.path.join(REPO, "test_output_dir2")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    test_file = _create_test_java_file(test_dir, "TestVariousRuntimeExceptions", test_code)

    result = _compile_test(test_dir, test_file)
    if result.returncode != 0:
        raise AssertionError(f"Compilation failed: {result.stderr}")

    cmd = ["java", "-cp", f"{test_dir}:{BAZEL_JAR}", "TestVariousRuntimeExceptions"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if "Results: 4/4" not in result.stdout:
        raise AssertionError(f"Not all runtime exceptions preserved:\n{result.stdout}\n{result.stderr}")


def test_checked_exception_still_wrapped():
    """
    Checked exceptions should still be wrapped in InitializationException.
    This ensures we don't break the existing behavior.
    """
    _ensure_bazel_build()

    test_code = '''
import org.openqa.selenium.concurrent.Lazy;
import org.openqa.selenium.concurrent.Lazy.InitializationException;

public class TestCheckedException {
    public static void main(String[] args) {
        Lazy<String> lazy = Lazy.lazy(() -> {
            throw new Exception("checked exception");
        });
        try {
            lazy.get();
            System.out.println("FAIL: Expected exception was not thrown");
            System.exit(1);
        } catch (InitializationException e) {
            if (e.getCause() instanceof Exception &&
                e.getCause().getMessage().equals("checked exception")) {
                System.out.println("PASS: Checked exception properly wrapped");
                System.exit(0);
            } else {
                System.out.println("FAIL: Wrong cause: " + e.getCause());
                System.exit(1);
            }
        } catch (Exception e) {
            System.out.println("FAIL: Checked exception not wrapped, got: " + e.getClass().getName());
            System.exit(1);
        }
    }
}
'''

    test_dir = os.path.join(REPO, "test_output_dir3")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    test_file = _create_test_java_file(test_dir, "TestCheckedException", test_code)

    result = _compile_test(test_dir, test_file)
    if result.returncode != 0:
        raise AssertionError(f"Compilation failed: {result.stderr}")

    cmd = ["java", "-cp", f"{test_dir}:{BAZEL_JAR}", "TestCheckedException"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if "PASS: Checked exception properly wrapped" not in result.stdout:
        raise AssertionError(f"Checked exception handling broken:\n{result.stdout}\n{result.stderr}")


def test_file_compiles():
    """
    Lazy.java should compile successfully (pass_to_pass).
    Compiles the concurrent package to verify the source is valid.
    """
    cmd = ["bazel", "build", "//java/src/org/openqa/selenium/concurrent:concurrent"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=REPO)
    if result.returncode != 0:
        raise AssertionError(f"Compile failed:\n{result.stderr[-1000:]}")


def test_bazel_build_concurrent():
    """
    Bazel build for the concurrent target should succeed.
    This is a pass_to_pass test using the repo's build system.
    """
    # Clean bazel cache to ensure fresh build
    cmd = ["bazel", "build", "//java/src/org/openqa/selenium/concurrent:concurrent"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=REPO)
    if result.returncode != 0:
        raise AssertionError(f"Bazel build failed:\n{result.stderr[-1000:]}")


def test_bazel_test_concurrent_smalltests():
    """
    Repo unit tests for concurrent package should pass (pass_to_pass).
    Runs //java/test/org/openqa/selenium/concurrent:SmallTests which includes LazyTest.
    """
    cmd = ["bazel", "test", "//java/test/org/openqa/selenium/concurrent:SmallTests"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=REPO)
    if result.returncode != 0:
        raise AssertionError(f"Bazel test failed:\n{result.stderr[-1000:]}")


def test_java_format():
    """
    Java code should be properly formatted according to repo style (pass_to_pass).
    Runs google-java-format check on the concurrent package.
    """
    # Run format on the concurrent package and check if there are changes
    lazy_java_path = os.path.join(REPO, "java/src/org/openqa/selenium/concurrent/Lazy.java")
    cmd = [
        "bazel", "run", "//scripts:google-java-format", "--",
        "--dry-run", "--set-exit-if-changed",
        lazy_java_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=REPO)
    # Exit code 0 means no formatting changes needed
    if result.returncode != 0:
        raise AssertionError(f"Java format check failed - code needs formatting:\n{result.stderr[-500:]}")


if __name__ == "__main__":
    # Run all test functions
    test_functions = [
        test_file_compiles,
        test_bazel_build_concurrent,
        test_bazel_test_concurrent_smalltests,
        test_java_format,
        test_runtime_exception_not_wrapped,
        test_various_runtime_exceptions,
        test_checked_exception_still_wrapped,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASS: {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test_func.__name__}: {e}")
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
