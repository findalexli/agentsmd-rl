#!/usr/bin/env python3
"""
Test outputs for Selenium .NET BiDi ReadOnlyMemory optimization task.

This tests:
1. ITransport.SendAsync signature uses ValueTask and ReadOnlyMemory<byte>
2. WebSocketTransport.SendAsync implementation uses proper conditional compilation
3. Broker.cs uses TrySetResult/TrySetException instead of SetResult/SetException
"""

import subprocess
import sys
import re
import os

REPO_ROOT = "/workspace/selenium"
DOTNET_BIDI_DIR = os.path.join(REPO_ROOT, "dotnet", "src", "webdriver", "BiDi")


def read_file(path):
    """Read file content."""
    with open(path, 'r') as f:
        return f.read()


def test_itransport_signature():
    """Test that ITransport.SendAsync uses ValueTask and ReadOnlyMemory<byte>."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "ITransport.cs"))

    # Should have ValueTask return type
    assert "ValueTask SendAsync" in content, "ITransport.SendAsync should return ValueTask"

    # Should have ReadOnlyMemory<byte> parameter
    assert "ReadOnlyMemory<byte> data" in content, "ITransport.SendAsync should accept ReadOnlyMemory<byte>"

    # Should NOT have old signature
    assert "Task SendAsync(byte[] data" not in content, "ITransport should not have old byte[] signature"

    print("✓ ITransport.SendAsync has correct signature with ValueTask and ReadOnlyMemory<byte>")


def test_websocket_transport_signature():
    """Test that WebSocketTransport.SendAsync matches the interface."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "WebSocketTransport.cs"))

    # Should have ValueTask return type
    assert "async ValueTask SendAsync" in content, "WebSocketTransport.SendAsync should return ValueTask"

    # Should have ReadOnlyMemory<byte> parameter
    assert "ReadOnlyMemory<byte> data" in content, "WebSocketTransport.SendAsync should accept ReadOnlyMemory<byte>"

    print("✓ WebSocketTransport.SendAsync has correct signature")


def test_websocket_transport_net8_optimization():
    """Test that WebSocketTransport uses .NET 8+ optimizations."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "WebSocketTransport.cs"))

    # Should have conditional compilation for NET8_0_OR_GREATER
    assert "#if NET8_0_OR_GREATER" in content, "Should have .NET 8+ conditional compilation"

    # Should use data.Span for logging in .NET 8+ path
    assert "Encoding.UTF8.GetString(data.Span)" in content, "Should use data.Span for logging in .NET 8+"

    # Should use direct data parameter for SendAsync in .NET 8+
    assert "_webSocket.SendAsync(data, WebSocketMessageType.Text" in content, \
        "Should use direct ReadOnlyMemory<byte> parameter for .NET 8+"

    print("✓ WebSocketTransport has .NET 8+ optimizations")


def test_websocket_transport_fallback():
    """Test that WebSocketTransport has fallback for older .NET versions."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "WebSocketTransport.cs"))

    # Should have #else branch for non-.NET 8
    assert "#else" in content, "Should have #else branch for older .NET versions"

    # Should use MemoryMarshal.TryGetArray for fallback
    assert "MemoryMarshal.TryGetArray" in content, "Should use MemoryMarshal.TryGetArray for fallback"

    # Should handle the segment extraction
    assert "ArraySegment<byte>" in content, "Should use ArraySegment<byte> for fallback"

    print("✓ WebSocketTransport has fallback for older .NET versions")


def test_broker_try_set_result():
    """Test that Broker.cs uses TrySetResult instead of SetResult."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "Broker.cs"))

    # Should use TrySetResult
    assert "TrySetResult" in content, "Broker should use TrySetResult"

    # Should NOT have SetResult on TaskCompletionSource (except in comments or other contexts)
    # Check that SetResult is not used on TaskCompletionSource
    lines = content.split('\n')
    for line in lines:
        if 'TaskCompletionSource' in line and 'SetResult' in line and 'TrySetResult' not in line:
            # Check if this is a comment
            stripped = line.strip()
            if not stripped.startswith('//'):
                assert False, f"Found SetResult without Try prefix: {line}"

    print("✓ Broker.cs uses TrySetResult")


def test_broker_try_set_exception():
    """Test that Broker.cs uses TrySetException instead of SetException."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "Broker.cs"))

    # Should use TrySetException
    assert "TrySetException" in content, "Broker should use TrySetException"

    # Check that SetException is not used on TaskCompletionSource (except in comments)
    lines = content.split('\n')
    for line in lines:
        if 'TaskCompletionSource' in line and 'SetException' in line and 'TrySetException' not in line:
            stripped = line.strip()
            if not stripped.startswith('//'):
                assert False, f"Found SetException without Try prefix: {line}"

    print("✓ Broker.cs uses TrySetException")


def test_compilation():
    """Test that the dotnet project compiles successfully."""
    result = subprocess.run(
        ["dotnet", "build", "dotnet/src/webdriver/WebDriver.csproj", "--no-restore", "-v:q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Note: We allow warnings but not errors
    if result.returncode != 0:
        print(f"Build stderr: {result.stderr}")
        print(f"Build stdout: {result.stdout}")

    assert result.returncode == 0, f"Build failed with exit code {result.returncode}"

    print("✓ Project compiles successfully")


def test_idempotency():
    """Test that the fix is idempotent - distinctive line from patch should be present."""
    content = read_file(os.path.join(DOTNET_BIDI_DIR, "Broker.cs"))

    # Check for the distinctive TrySetResult line
    assert "command.TaskCompletionSource.TrySetResult" in content, \
        "Idempotency check: TrySetResult not found in Broker.cs"

    print("✓ Idempotency check passed")


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_itransport_signature,
        test_websocket_transport_signature,
        test_websocket_transport_net8_optimization,
        test_websocket_transport_fallback,
        test_broker_try_set_result,
        test_broker_try_set_exception,
        test_compilation,
        test_idempotency,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)
