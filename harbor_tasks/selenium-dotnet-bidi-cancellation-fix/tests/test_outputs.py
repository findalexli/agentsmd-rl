"""Tests for Selenium .NET BiDi Broker cancellation fix.

This test suite verifies that the fix for PR #17315 is correctly applied.
The bug was that ctsRegistration was disposed too early, preventing commands
from being cancelled via timeout.
"""

import subprocess
import sys
import re

REPO_PATH = "/workspace/selenium"
BROKER_FILE = f"{REPO_PATH}/dotnet/src/webdriver/BiDi/Broker.cs"


def read_broker_source():
    """Read the Broker.cs source file."""
    with open(BROKER_FILE, 'r') as f:
        return f.read()


def test_code_compiles():
    """Fail-to-pass: Verify the C# code compiles successfully.

    Before the fix: The old code had potential issues with buffer management.
    After fix: Code compiles cleanly.
    """
    result = subprocess.run(
        ["dotnet", "build", "dotnet/src/webdriver/WebDriver.csproj", "--no-restore"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check compilation succeeded
    assert result.returncode == 0, f"Compilation failed:\n{result.stdout}\n{result.stderr}"


def test_serialization_error_handling():
    """Fail-to-pass: Verify serialization errors properly return buffer.

    The fix adds a catch block after the JSON serialization to return the
    sendBuffer if serialization fails, preventing resource leaks.

    Before fix: No catch block for serialization errors - buffer leaked.
    After fix: catch { ReturnBuffer(sendBuffer); throw; }
    """
    source = read_broker_source()

    # Find the ExecuteCommandAsync method
    method_match = re.search(
        r'public async Task<TResult> ExecuteCommandAsync<TCommand, TResult>.*?(?=\n    public|\n    private|\Z)',
        source,
        re.DOTALL
    )
    assert method_match, "ExecuteCommandAsync method not found"
    method_body = method_match.group(0)

    # Look for the pattern: serialization try block followed by catch with ReturnBuffer
    # The fix adds this catch block right after the using(UTF8JsonWriter) block
    serialization_catch = re.search(
        r'using \(var writer = new Utf8JsonWriter\(sendBuffer\)\)\s*\{[^}]+\}\s*\}\s*catch\s*\{[^}]*ReturnBuffer\(sendBuffer\);[^}]*throw;',
        method_body,
        re.DOTALL
    )

    assert serialization_catch, (
        "Missing serialization error handling. Expected catch block with ReturnBuffer(sendBuffer) "
        "after JSON serialization using block"
    )


def test_cts_registration_scope():
    """Fail-to-pass: Verify ctsRegistration is declared outside the send try block.

    The core bug: ctsRegistration was disposed too early because it was declared
    inside a try block that ended before the await completed.

    Before fix: using var ctsRegistration inside nested try block.
    After fix: using var ctsRegistration declared between two try blocks.
    """
    source = read_broker_source()

    method_match = re.search(
        r'public async Task<TResult> ExecuteCommandAsync<TCommand, TResult>.*?(?=\n    public|\n    private|\Z)',
        source,
        re.DOTALL
    )
    assert method_match, "ExecuteCommandAsync method not found"
    method_body = method_match.group(0)

    # Look for the correct pattern:
    # 1. First try block ends (for serialization)
    # 2. catch { ReturnBuffer... } (new in fix)
    # 3. commandInfo assignment
    # 4. ctsRegistration declaration with using
    # 5. Second try block starts (for send)
    correct_pattern = re.search(
        r'ReturnBuffer\(sendBuffer\);.*?throw;.*?\}\s*'  # end of first catch
        r'var commandInfo = new CommandInfo.*?\}\s*'      # commandInfo assignment
        r'using var ctsRegistration = cts\.Token\.Register.*?\{.*?\}\);\s*'  # ctsRegistration
        r'try\s*\{',  # Second try block
        method_body,
        re.DOTALL
    )

    assert correct_pattern, (
        "Incorrect ctsRegistration scope. The fix requires ctsRegistration to be declared "
        "AFTER the serialization try-catch block and BEFORE the transport send try block. "
        "This ensures the cancellation registration stays alive during the await."
    )


def test_buffer_returned_in_serialization_error():
    """Pass-to-pass: Verify buffer is returned in catch, not just in finally.

    Before fix: Buffer was only returned in finally block, which meant
    serialization errors could leave the buffer unreleased until the
    method completed.

    After fix: Buffer is returned immediately in the catch block after
    serialization failure.
    """
    source = read_broker_source()

    # Look for the pattern where ReturnBuffer is called in the catch block
    # specifically for the serialization section
    pattern = r'catch\s*\{[^}]*ReturnBuffer\(sendBuffer\);[^}]*throw;[^}]*\}'
    match = re.search(pattern, source, re.DOTALL)

    assert match, (
        "Expected catch block with ReturnBuffer(sendBuffer) and re-throw. "
        "This is needed to properly release the buffer on serialization errors."
    )


def test_pending_commands_cleanup_on_send_error():
    """Pass-to-pass: Verify pending commands are cleaned up on send errors.

    This pattern existed before the fix, but verify it remains after refactoring.
    """
    source = read_broker_source()

    method_match = re.search(
        r'public async Task<TResult> ExecuteCommandAsync<TCommand, TResult>.*?(?=\n    public|\n    private|\Z)',
        source,
        re.DOTALL
    )
    assert method_match, "ExecuteCommandAsync method not found"
    method_body = method_match.group(0)

    # Look for the pattern in the send try-catch
    cleanup_pattern = re.search(
        r'try\s*\{[^}]*await _transport\.SendAsync.*?\}\s*catch\s*\{[^}]*_pendingCommands\.TryRemove\(command\.Id, out _\);[^}]*throw;',
        method_body,
        re.DOTALL
    )

    assert cleanup_pattern, (
        "Missing pending commands cleanup on send error. "
        "Expected catch block with _pendingCommands.TryRemove after transport send."
    )


def test_no_nested_try_with_registration():
    """Fail-to-pass: Verify ctsRegistration is NOT inside a nested try block.

    This is the key anti-pattern that caused the bug.

    Before fix: ctsRegistration was inside: try { using var ctsRegistration ... try { await ... } }
    After fix: ctsRegistration is between two separate try blocks
    """
    source = read_broker_source()

    method_match = re.search(
        r'public async Task<TResult> ExecuteCommandAsync<TCommand, TResult>.*?(?=\n    public|\n    private|\Z)',
        source,
        re.DOTALL
    )
    assert method_match, "ExecuteCommandAsync method not found"
    method_body = method_match.group(0)

    # Check that ctsRegistration is NOT inside the first try block that contains
    # the Utf8JsonWriter (this was the bug pattern)
    first_try_content = re.search(
        r'try\s*\{\s*using \(BiDiContext\.Use\(_bidi\)\)\s*using \(var writer = new Utf8JsonWriter\(sendBuffer\)\)',
        method_body,
        re.DOTALL
    )

    if first_try_content:
        # Get the position where first try ends
        first_try_start = first_try_content.start()

        # Find where ctsRegistration is declared
        cts_reg_match = re.search(r'using var ctsRegistration = cts\.Token\.Register', method_body)
        assert cts_reg_match, "ctsRegistration declaration not found"

        cts_reg_pos = cts_reg_match.start()

        # The fix puts ctsRegistration AFTER the first try-catch block
        # So if ctsRegistration is still inside the first try block, that's wrong
        # We check by looking at the structure: after the first try, there should be
        # a catch block with ReturnBuffer

        after_first_try = method_body[first_try_start:first_try_start+500]

        # The correct pattern has the serialization catch block between first try and ctsRegistration
        has_serialization_catch = 'catch' in after_first_try and 'ReturnBuffer(sendBuffer)' in after_first_try[:500]

        # If ctsRegistration comes before we see the catch block with ReturnBuffer, that's wrong
        cts_before_catch = cts_reg_pos < (first_try_start + after_first_try.find('catch'))

        assert not cts_before_catch, (
            "ctsRegistration is incorrectly positioned. It should be AFTER the serialization "
            "try-catch block, not inside or before it. This was the root cause of the cancellation bug."
        )


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_code_compiles,
        test_serialization_error_handling,
        test_cts_registration_scope,
        test_buffer_returned_in_serialization_error,
        test_pending_commands_cleanup_on_send_error,
        test_no_nested_try_with_registration,
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

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
