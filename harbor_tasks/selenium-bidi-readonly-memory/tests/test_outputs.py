"""
Test outputs for the Selenium BiDi ReadOnlyMemory optimization PR.
Tests that the transport interface is updated to use ReadOnlyMemory<byte>
and that TrySetResult/TrySetException are used for thread safety.
"""

import subprocess
import sys
import os
import pytest

REPO = "/workspace/selenium"
DOTNET_DIR = os.path.join(REPO, "dotnet")
WEBDRIVER_DIR = os.path.join(DOTNET_DIR, "src/webdriver")


def test_transport_interface_uses_readonly_memory():
    """
    Fail-to-pass: ITransport.SendAsync must accept ReadOnlyMemory<byte> instead of byte[].

    This test verifies the interface signature was updated per the PR.
    """
    transport_file = os.path.join(WEBDRIVER_DIR, "BiDi/ITransport.cs")
    with open(transport_file, 'r') as f:
        content = f.read()

    # Should use ReadOnlyMemory<byte> not byte[]
    assert "ReadOnlyMemory<byte>" in content, "ITransport should use ReadOnlyMemory<byte>"
    # Should NOT have the old signature with byte[]
    assert "SendAsync(byte[] data" not in content, "ITransport should not use byte[] signature"


def test_transport_returns_value_task():
    """
    Fail-to-pass: ITransport.SendAsync must return ValueTask not Task.

    ReadOnlyMemory optimizations are best paired with ValueTask to reduce allocations.
    """
    transport_file = os.path.join(WEBDRIVER_DIR, "BiDi/ITransport.cs")
    with open(transport_file, 'r') as f:
        content = f.read()

    # Should return ValueTask
    assert "ValueTask SendAsync" in content, "ITransport.SendAsync should return ValueTask"
    # Should NOT return Task
    assert "Task SendAsync(byte[]" not in content, "ITransport should not return Task with byte[]"


def test_websocket_transport_implements_interface():
    """
    Fail-to-pass: WebSocketTransport must implement the updated interface.

    Verifies the concrete implementation matches the interface signature.
    """
    ws_file = os.path.join(WEBDRIVER_DIR, "BiDi/WebSocketTransport.cs")
    with open(ws_file, 'r') as f:
        content = f.read()

    # Should have ValueTask signature with ReadOnlyMemory
    assert "ValueTask SendAsync(ReadOnlyMemory<byte> data" in content, \
        "WebSocketTransport.SendAsync should use ValueTask with ReadOnlyMemory<byte>"


def test_websocket_has_conditional_compilation_for_net8():
    """
    Fail-to-pass: WebSocketTransport must use conditional compilation for .NET 8 optimization.

    The PR adds optimized path for .NET 8+ while maintaining compatibility.
    """
    ws_file = os.path.join(WEBDRIVER_DIR, "BiDi/WebSocketTransport.cs")
    with open(ws_file, 'r') as f:
        content = f.read()

    # Should have the NET8_0_OR_GREATER conditional
    assert "#if NET8_0_OR_GREATER" in content, \
        "WebSocketTransport should have conditional compilation for .NET 8+"
    assert "#else" in content, \
        "WebSocketTransport should have else branch for older .NET versions"
    assert "#endif" in content, \
        "WebSocketTransport should close conditional compilation"


def test_broker_uses_try_set_result():
    """
    Fail-to-pass: Broker must use TrySetResult instead of SetResult.

    Thread safety fix - TrySetResult prevents exceptions if task already completed.
    """
    broker_file = os.path.join(WEBDRIVER_DIR, "BiDi/Broker.cs")
    with open(broker_file, 'r') as f:
        content = f.read()

    # Should use TrySetResult
    assert "TrySetResult" in content, "Broker should use TrySetResult for thread safety"
    # Should NOT use plain SetResult in the completion path
    lines = content.split('\n')
    for line in lines:
        if 'SetResult' in line and 'TrySetResult' not in line:
            assert False, f"Found unsafe SetResult usage: {line.strip()}"


def test_broker_uses_try_set_exception():
    """
    Fail-to-pass: Broker must use TrySetException instead of SetException.

    Thread safety fix - TrySetException prevents exceptions if task already completed.
    """
    broker_file = os.path.join(WEBDRIVER_DIR, "BiDi/Broker.cs")
    with open(broker_file, 'r') as f:
        content = f.read()

    # Should use TrySetException
    assert "TrySetException" in content, "Broker should use TrySetException for thread safety"


def test_dotnet_syntax_valid():
    """
    Pass-to-pass: The dotnet BiDi code should have valid C# syntax.

    Uses 'dotnet build' with --no-restore and checks specifically for
    compilation errors in the BiDi files we care about.
    Skipped if Bazel is not available (Selenium Manager dependency).
    """
    import shutil

    # Check if bazel is available
    if shutil.which("bazel") is None:
        pytest.skip("Bazel not available - required for full build")

    result = subprocess.run(
        ["dotnet", "build", "src/webdriver/Selenium.WebDriver.csproj", "-c", "Release"],
        cwd=DOTNET_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, f"Build failed:\n{result.stderr[-1000:]}"


def test_no_compile_errors_in_bidi():
    """
    Pass-to-pass: BiDi code specifically must compile without errors.

    Runs dotnet build and checks for any errors in BiDi namespace.
    Skipped if Bazel is not available (Selenium Manager dependency).
    """
    import shutil

    # Check if bazel is available
    if shutil.which("bazel") is None:
        pytest.skip("Bazel not available - required for full build")

    result = subprocess.run(
        ["dotnet", "build", "src/webdriver/Selenium.WebDriver.csproj", "-c", "Release"],
        cwd=DOTNET_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    output = result.stdout + result.stderr
    # Check for any BiDi-related compilation errors
    if "BiDi" in output and ("error" in output.lower() or result.returncode != 0):
        # Extract BiDi-related error lines
        lines = output.split('\n')
        bidi_errors = [l for l in lines if 'BiDi' in l and 'error' in l.lower()]
        if bidi_errors:
            assert False, f"BiDi compilation errors found:\n" + '\n'.join(bidi_errors[:10])

    assert result.returncode == 0, f"Build failed with return code {result.returncode}"


def test_dotnet_bidi_formatting():
    """
    Pass-to-pass: BiDi code must follow dotnet formatting rules.

    Uses 'dotnet format --verify-no-changes' to check BiDi files
    follow editorconfig style rules. This is a pass-to-pass test
    that ensures the gold patch doesn't introduce formatting issues.
    """
    # First check if dotnet format is available
    check = subprocess.run(
        ["dotnet", "format", "--version"],
        cwd=DOTNET_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )
    if check.returncode != 0:
        pytest.skip("dotnet format not available")

    result = subprocess.run(
        ["dotnet", "format", "src/webdriver/Selenium.WebDriver.csproj",
         "--verify-no-changes", "--include",
         "src/webdriver/BiDi/ITransport.cs",
         "src/webdriver/BiDi/WebSocketTransport.cs",
         "src/webdriver/BiDi/Broker.cs"],
        cwd=DOTNET_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Formatting check failed:\n{result.stderr[-1000:]}"


def test_dotnet_project_files_valid():
    """
    Pass-to-pass: .csproj files must be valid XML and parseable.

    Validates that the project files are well-formed XML
    and can be read by dotnet CLI tools without errors.
    """
    import xml.etree.ElementTree as ET

    proj_files = [
        os.path.join(WEBDRIVER_DIR, "Selenium.WebDriver.csproj"),
        os.path.join(DOTNET_DIR, "src/support/Selenium.WebDriver.Support.csproj"),
    ]

    for proj_file in proj_files:
        if os.path.exists(proj_file):
            try:
                tree = ET.parse(proj_file)
                root = tree.getroot()
                # Verify it has basic Project structure
                assert root.tag.endswith("Project") or root.tag == "Project", \
                    f"{proj_file}: Missing Project root element"
            except ET.ParseError as e:
                assert False, f"{proj_file}: Invalid XML - {e}"


def test_bidi_files_have_valid_cs_syntax():
    """
    Pass-to-pass: BiDi C# files must have valid syntax structure.

    Uses 'dotnet format --verify-no-changes --severity error' to check
    for syntax errors in BiDi files. This is a lighter check than full build.
    """
    # First check if dotnet format is available
    check = subprocess.run(
        ["dotnet", "format", "--version"],
        cwd=DOTNET_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )
    if check.returncode != 0:
        pytest.skip("dotnet format not available")

    result = subprocess.run(
        ["dotnet", "format", "src/webdriver/Selenium.WebDriver.csproj",
         "--verify-no-changes", "--severity", "error",
         "--include",
         "src/webdriver/BiDi/ITransport.cs",
         "src/webdriver/BiDi/WebSocketTransport.cs",
         "src/webdriver/BiDi/Broker.cs"],
        cwd=DOTNET_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Only fail on actual errors, not warnings
    if result.returncode != 0:
        error_output = result.stderr[-1000:] if result.stderr else result.stdout[-1000:]
        assert False, f"Syntax errors found:\n{error_output}"
