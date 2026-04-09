"""
Tests for verifying the Lazy.java RuntimeException fix.

The fix ensures RuntimeExceptions are re-thrown directly rather than being
wrapped in InitializationException, allowing proper exception propagation.
"""

import subprocess
import os
import sys

REPO = "/workspace/selenium"
LAZY_JAVA = "java/src/org/openqa/selenium/concurrent/Lazy.java"


def test_runtime_exception_not_wrapped():
    """
    Fail-to-pass: RuntimeException should be thrown as-is, not wrapped.

    The bug was that RuntimeExceptions were caught by the generic Exception
    handler and wrapped in InitializationException. The fix adds a specific
    RuntimeException catch that re-throws without wrapping.
    """
    test_code = """
import java.io.*;
import java.nio.file.*;

public class TestRuntimeExceptionPropagation {
    public static void main(String[] args) throws Exception {
        // Read the Lazy.java source
        String content = Files.readString(Path.of("java/src/org/openqa/selenium/concurrent/Lazy.java"));

        // Check that RuntimeException is specifically caught and re-thrown
        boolean hasRuntimeExceptionCatch = content.contains("catch (RuntimeException e)") &&
                                             content.contains("throw e;");

        if (!hasRuntimeExceptionCatch) {
            System.err.println("FAIL: RuntimeException is not properly caught and re-thrown");
            System.exit(1);
        }

        // Verify the order: RuntimeException catch comes BEFORE generic Exception catch
        int rteCatchPos = content.indexOf("catch (RuntimeException e)");
        int genericCatchPos = content.indexOf("catch (Exception e)");

        if (rteCatchPos == -1 || genericCatchPos == -1 || rteCatchPos > genericCatchPos) {
            System.err.println("FAIL: RuntimeException catch must come before generic Exception catch");
            System.exit(1);
        }

        System.out.println("PASS: RuntimeException is properly re-thrown without wrapping");
    }
}
"""
    # Write and compile test
    test_file = "/tmp/TestRuntimeExceptionPropagation.java"
    with open(test_file, "w") as f:
        f.write(test_code)

    compile = subprocess.run(
        ["javac", test_file],
        capture_output=True,
        text=True
    )
    assert compile.returncode == 0, f"Compilation failed: {compile.stderr}"

    # Run test
    run = subprocess.run(
        ["java", "-cp", "/tmp", "TestRuntimeExceptionPropagation"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert run.returncode == 0, f"Test failed: {run.stderr}"


def test_lazy_initialization_behavior():
    """
    Functional test: Verify Lazy.get() throws RuntimeException directly.

    We compile the Lazy class and test that RuntimeExceptions propagate
    through without being wrapped in InitializationException.
    """
    # First, let's verify the code compiles
    compile = subprocess.run(
        ["javac", "-d", "/tmp/lazy_classes",
         "java/src/org/openqa/selenium/concurrent/Lazy.java",
         "java/src/org/openqa/selenium/concurrent/InitializationException.java"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert compile.returncode == 0, f"Lazy.java compilation failed: {compile.stderr}"

    # Create a test that verifies the exception behavior
    test_code = """
import org.openqa.selenium.concurrent.Lazy;
import org.openqa.selenium.concurrent.InitializationException;

public class TestLazyRTEBehavior {
    public static void main(String[] args) {
        // Test 1: RuntimeException should propagate as-is
        Lazy<String> lazyRTE = new Lazy<>(() -> {
            throw new IllegalStateException("test runtime exception");
        });

        try {
            lazyRTE.get();
            System.err.println("FAIL: Expected exception was not thrown");
            System.exit(1);
        } catch (IllegalStateException e) {
            // Expected - RTE propagated directly
            if (!e.getMessage().equals("test runtime exception")) {
                System.err.println("FAIL: Wrong exception message: " + e.getMessage());
                System.exit(1);
            }
        } catch (InitializationException e) {
            System.err.println("FAIL: RuntimeException was wrapped in InitializationException");
            System.exit(1);
        }

        // Test 2: Checked exceptions should still be wrapped
        Lazy<String> lazyChecked = new Lazy<>(() -> {
            throw new java.io.IOException("test checked exception");
        });

        try {
            lazyChecked.get();
            System.err.println("FAIL: Expected exception was not thrown");
            System.exit(1);
        } catch (InitializationException e) {
            // Expected - checked exception wrapped
            if (!(e.getCause() instanceof java.io.IOException)) {
                System.err.println("FAIL: Wrong cause type for checked exception: " + e.getCause());
                System.exit(1);
            }
        } catch (IllegalStateException e) {
            System.err.println("FAIL: Checked exception should not be thrown as RTE");
            System.exit(1);
        }

        System.out.println("PASS: Lazy correctly handles RuntimeException vs checked exceptions");
    }
}
"""
    test_file = "/tmp/TestLazyRTEBehavior.java"
    with open(test_file, "w") as f:
        f.write(test_code)

    compile = subprocess.run(
        ["javac", "-cp", "/tmp/lazy_classes", test_file],
        capture_output=True,
        text=True
    )
    assert compile.returncode == 0, f"Test compilation failed: {compile.stderr}"

    run = subprocess.run(
        ["java", "-cp", "/tmp/lazy_classes:/tmp", "TestLazyRTEBehavior"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert run.returncode == 0, f"Behavior test failed: {run.stderr}"


def test_code_structure_integrity():
    """
    Verify the fix doesn't break surrounding code structure.

    Checks that the try-catch structure is preserved with the new catch block
    inserted in the correct position.
    """
    with open(os.path.join(REPO, LAZY_JAVA), "r") as f:
        content = f.read()

    # Verify the overall structure exists
    required_patterns = [
        "try {",
        "value = supplier.get();",
        "catch (RuntimeException e)",
        "throw e;",
        "catch (Exception e)",
        "throw new InitializationException(e);"
    ]

    for pattern in required_patterns:
        assert pattern in content, f"Required pattern missing: {pattern}"

    # Verify synchronization structure is intact
    assert "synchronized (this)" in content, "Synchronization block missing"
    assert "if (value == null)" in content, "Double-checked locking pattern missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
