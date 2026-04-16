"""
Test suite for selenium-keys-charsequence-contract task.
Tests that Keys.charAt() enforces the CharSequence contract by throwing
IndexOutOfBoundsException for invalid indexes instead of returning 0.
"""
import subprocess
import os
import tempfile

REPO = "/workspace/selenium"


def compile_and_run_java(java_code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Compile and run Java code that tests Keys behavior."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write the test file
        test_file = os.path.join(tmpdir, "KeysCharAtTest.java")
        with open(test_file, "w") as f:
            f.write(java_code)

        # Compile Keys.java first
        keys_src = os.path.join(REPO, "java/src/org/openqa/selenium/Keys.java")

        # Create package directory structure
        pkg_dir = os.path.join(tmpdir, "org/openqa/selenium")
        os.makedirs(pkg_dir, exist_ok=True)

        # Compile Keys.java (strip jspecify import which we don't have)
        with open(keys_src) as f:
            keys_content = f.read()
        # Remove jspecify import and annotation since we don't have that dependency
        keys_content = keys_content.replace("import org.jspecify.annotations.Nullable;", "")
        keys_content = keys_content.replace("@Nullable ", "")

        keys_file = os.path.join(pkg_dir, "Keys.java")
        with open(keys_file, "w") as f:
            f.write(keys_content)

        # Compile
        compile_result = subprocess.run(
            ["javac", "-d", tmpdir, keys_file, test_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if compile_result.returncode != 0:
            return compile_result

        # Run
        return subprocess.run(
            ["java", "-cp", tmpdir, "KeysCharAtTest"],
            capture_output=True,
            text=True,
            timeout=timeout
        )


def test_charat_invalid_index_throws_exception():
    """
    Keys.charAt(1) should throw IndexOutOfBoundsException.
    Bug: on base commit, it returns 0 (null char) instead of throwing.
    This is fail_to_pass.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        try {
            char result = Keys.ENTER.charAt(1);
            // If we get here, no exception was thrown - this is the bug
            System.out.println("FAIL: Expected IndexOutOfBoundsException but got char: " + (int)result);
            System.exit(1);
        } catch (IndexOutOfBoundsException e) {
            System.out.println("PASS: IndexOutOfBoundsException thrown as expected");
            System.exit(0);
        } catch (Exception e) {
            System.out.println("FAIL: Wrong exception type: " + e.getClass().getName());
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_charat_negative_index_throws_exception():
    """
    Keys.charAt(-1) should throw IndexOutOfBoundsException.
    Bug: on base commit, it returns 0 (null char) instead of throwing.
    This is fail_to_pass.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        try {
            char result = Keys.TAB.charAt(-1);
            System.out.println("FAIL: Expected IndexOutOfBoundsException but got char: " + (int)result);
            System.exit(1);
        } catch (IndexOutOfBoundsException e) {
            System.out.println("PASS: IndexOutOfBoundsException thrown for negative index");
            System.exit(0);
        } catch (Exception e) {
            System.out.println("FAIL: Wrong exception type: " + e.getClass().getName());
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_charat_large_index_throws_exception():
    """
    Keys.charAt(100) should throw IndexOutOfBoundsException.
    Bug: on base commit, it returns 0 (null char) instead of throwing.
    This is fail_to_pass.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        try {
            char result = Keys.SHIFT.charAt(100);
            System.out.println("FAIL: Expected IndexOutOfBoundsException but got char: " + (int)result);
            System.exit(1);
        } catch (IndexOutOfBoundsException e) {
            System.out.println("PASS: IndexOutOfBoundsException thrown for large index");
            System.exit(0);
        } catch (Exception e) {
            System.out.println("FAIL: Wrong exception type: " + e.getClass().getName());
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_charat_zero_returns_keycode():
    """
    Keys.charAt(0) should return the key code.
    This is pass_to_pass - should work before and after fix.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        // ENTER has keyCode '\\uE007'
        char result = Keys.ENTER.charAt(0);
        int expected = 0xE007;
        if (result == expected) {
            System.out.println("PASS: charAt(0) returns correct keyCode");
            System.exit(0);
        } else {
            System.out.println("FAIL: Expected " + expected + " but got " + (int)result);
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_multiple_keys_charat_zero():
    """
    Verify charAt(0) works correctly for multiple different Keys.
    This is pass_to_pass.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        // Test multiple keys
        boolean allPassed = true;

        // LEFT has keyCode '\\uE012'
        if (Keys.LEFT.charAt(0) != '\\uE012') {
            System.out.println("FAIL: LEFT.charAt(0) incorrect");
            allPassed = false;
        }

        // TAB has keyCode '\\uE004'
        if (Keys.TAB.charAt(0) != '\\uE004') {
            System.out.println("FAIL: TAB.charAt(0) incorrect");
            allPassed = false;
        }

        // ESCAPE has keyCode '\\uE00C'
        if (Keys.ESCAPE.charAt(0) != '\\uE00C') {
            System.out.println("FAIL: ESCAPE.charAt(0) incorrect");
            allPassed = false;
        }

        if (allPassed) {
            System.out.println("PASS: All keys return correct charAt(0)");
            System.exit(0);
        } else {
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_charsequence_contract_length():
    """
    Verify length() returns 1 for all Keys.
    This is pass_to_pass.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        for (Keys key : Keys.values()) {
            if (key.length() != 1) {
                System.out.println("FAIL: " + key.name() + ".length() = " + key.length());
                System.exit(1);
            }
        }
        System.out.println("PASS: All keys have length 1");
        System.exit(0);
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_keys_java_compiles():
    """
    Keys.java compiles successfully (pass_to_pass).
    Verifies the source file has valid Java syntax.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        keys_src = os.path.join(REPO, "java/src/org/openqa/selenium/Keys.java")

        # Create package directory structure
        pkg_dir = os.path.join(tmpdir, "org/openqa/selenium")
        os.makedirs(pkg_dir, exist_ok=True)

        # Read and strip jspecify dependency
        with open(keys_src) as f:
            keys_content = f.read()
        keys_content = keys_content.replace("import org.jspecify.annotations.Nullable;", "")
        keys_content = keys_content.replace("@Nullable ", "")

        keys_file = os.path.join(pkg_dir, "Keys.java")
        with open(keys_file, "w") as f:
            f.write(keys_content)

        # Compile
        result = subprocess.run(
            ["javac", "-d", tmpdir, keys_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Keys.java compilation failed:\n{result.stderr}"


def test_keys_enum_has_expected_values():
    """
    Keys enum contains expected key constants (pass_to_pass).
    Tests that fundamental Keys values exist and have correct codes.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        // Test that expected Keys constants exist
        boolean allPassed = true;

        // NULL should be \\uE000
        if (Keys.NULL.charAt(0) != '\\uE000') {
            System.out.println("FAIL: NULL keyCode incorrect");
            allPassed = false;
        }

        // ENTER should be \\uE007
        if (Keys.ENTER.charAt(0) != '\\uE007') {
            System.out.println("FAIL: ENTER keyCode incorrect");
            allPassed = false;
        }

        // SHIFT should be \\uE008
        if (Keys.SHIFT.charAt(0) != '\\uE008') {
            System.out.println("FAIL: SHIFT keyCode incorrect");
            allPassed = false;
        }

        // CONTROL should be \\uE009
        if (Keys.CONTROL.charAt(0) != '\\uE009') {
            System.out.println("FAIL: CONTROL keyCode incorrect");
            allPassed = false;
        }

        // ALT should be \\uE00A
        if (Keys.ALT.charAt(0) != '\\uE00A') {
            System.out.println("FAIL: ALT keyCode incorrect");
            allPassed = false;
        }

        if (allPassed) {
            System.out.println("PASS: All expected Keys constants have correct codes");
            System.exit(0);
        } else {
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"


def test_keys_subsequence_valid():
    """
    Keys.subSequence(0,1) returns correct CharSequence (pass_to_pass).
    Tests CharSequence contract compliance.
    """
    java_code = '''
import org.openqa.selenium.Keys;

public class KeysCharAtTest {
    public static void main(String[] args) {
        boolean allPassed = true;

        // Test subSequence for a few keys
        for (Keys key : new Keys[] {Keys.ENTER, Keys.TAB, Keys.ESCAPE, Keys.SHIFT}) {
            CharSequence sub = key.subSequence(0, 1);
            if (sub.length() != 1) {
                System.out.println("FAIL: " + key.name() + ".subSequence(0,1).length() != 1");
                allPassed = false;
            }
            if (sub.charAt(0) != key.charAt(0)) {
                System.out.println("FAIL: " + key.name() + ".subSequence(0,1).charAt(0) mismatch");
                allPassed = false;
            }
        }

        if (allPassed) {
            System.out.println("PASS: subSequence returns correct CharSequence");
            System.exit(0);
        } else {
            System.exit(1);
        }
    }
}
'''
    result = compile_and_run_java(java_code)
    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"
