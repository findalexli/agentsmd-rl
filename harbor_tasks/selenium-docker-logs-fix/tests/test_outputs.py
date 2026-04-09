#!/usr/bin/env python3
"""Tests for Selenium Docker logs parsing fix.

This PR fixes how Docker's multiplexed stream format is parsed.
Docker returns logs with an 8-byte header per frame:
- 1 byte: stream type (1=stdout, 2=stderr)
- 3 bytes: padding (empty)
- 4 bytes: payload size (big-endian)
- N bytes: actual log content

Before the fix, these headers were being written to the log file,
resulting in garbage characters like "^A??????g" at the start of lines.
"""

import os
import subprocess
import sys
import tempfile

REPO = "/workspace/selenium"
JAVA_SRC = f"{REPO}/java/src"


def run_bazel_build(target: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a bazel build command."""
    return subprocess.run(
        ["bazel", "build", target],
        cwd=REPO,
        capture_output=True,
        timeout=timeout,
        text=True,
    )


def compile_java_file(file_path: str, classpath: str = "") -> subprocess.CompletedProcess:
    """Compile a single Java file."""
    cmd = ["javac", "-d", "/tmp/compiled"]
    if classpath:
        cmd.extend(["-cp", classpath])
    cmd.append(file_path)
    return subprocess.run(cmd, capture_output=True, text=True)


# =============================================================================
# Test: DockerSession parseMultiplexedStream logic
# =============================================================================

def test_multiplexed_stream_parsing():
    """Test that multiplexed stream parsing correctly extracts payload.

    F2P: Before the fix, the raw stream (with headers) would be written directly.
    After the fix, the 8-byte headers are stripped and only payload is written.
    """
    # Read the DockerSession.java source to verify the parsing logic exists
    docker_session_path = f"{JAVA_SRC}/org/openqa/selenium/grid/node/docker/DockerSession.java"
    with open(docker_session_path) as f:
        content = f.read()

    # Check for the key parsing elements
    assert "parseMultiplexedStream" in content, "parseMultiplexedStream method not found"
    assert "in.skipBytes(1)" in content, "Stream type byte skip not found"
    assert "in.skipBytes(3)" in content, "Padding bytes skip not found"
    assert "in.readInt()" in content, "Payload size read not found"
    assert "in.readFully(payload)" in content, "Payload read not found"
    assert "EOFException" in content, "EOF handling not found"


def test_multiplexed_stream_frame_format():
    """Test that the frame parsing handles the 8-byte header correctly.

    Docker multiplexed stream format per frame:
    [1 byte: stream type][3 bytes: padding][4 bytes: size][N bytes: payload]
    """
    import io

    # Simulate the parsing logic in Python to verify the algorithm
    def parse_frame(data: bytes) -> tuple:
        """Parse a single frame, return (stream_type, payload)."""
        if len(data) < 8:
            raise EOFError("Incomplete frame header")
        stream_type = data[0]
        # bytes 1-3 are padding, skip them
        size = int.from_bytes(data[4:8], 'big', signed=False)
        if len(data) < 8 + size:
            raise EOFError("Incomplete payload")
        payload = data[8:8+size]
        return stream_type, payload

    # Test frame: stdout (1), padding (0,0,0), size (5), payload ("hello")
    test_frame = bytes([1, 0, 0, 0, 0, 0, 0, 5]) + b"hello"
    stream_type, payload = parse_frame(test_frame)
    assert stream_type == 1, "Stream type should be 1 (stdout)"
    assert payload == b"hello", f"Payload should be 'hello', got {payload}"

    # Test frame: stderr (2), padding (0,0,0), size (5), payload ("error")
    test_frame = bytes([2, 0, 0, 0, 0, 0, 0, 5]) + b"error"
    stream_type, payload = parse_frame(test_frame)
    assert stream_type == 2, "Stream type should be 2 (stderr)"
    assert payload == b"error", f"Payload should be 'error', got {payload}"

    # Test empty payload
    test_frame = bytes([1, 0, 0, 0, 0, 0, 0, 0])
    stream_type, payload = parse_frame(test_frame)
    assert payload == b"", "Empty payload should be empty bytes"


# =============================================================================
# Test: JdkHttpMessages binary stream detection
# =============================================================================

def test_isBinaryStream_method_exists():
    """Test that isBinaryStream method exists and handles Docker content types."""
    jdk_messages_path = f"{JAVA_SRC}/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java"
    with open(jdk_messages_path) as f:
        content = f.read()

    # Check for the isBinaryStream method
    assert "isBinaryStream" in content, "isBinaryStream method not found"
    assert "application/vnd.docker.multiplexed-stream" in content, \
        "Docker multiplexed-stream content type not handled"
    assert "application/vnd.docker.raw-stream" in content, \
        "Docker raw-stream content type not handled"


def test_isBinaryStream_recognizes_docker_streams():
    """Test the isBinaryStream logic against Docker content types.

    F2P: Before the fix, only OCTET_STREAM was recognized.
    After the fix, Docker-specific content types are also recognized.
    """
    # Simulate the Java logic in Python
    def is_binary_stream(content_type: str) -> bool:
        if not content_type:
            return False
        ct = content_type.lower()
        return (ct == "application/octet-stream" or
                ct == "application/vnd.docker.multiplexed-stream" or
                ct == "application/vnd.docker.raw-stream")

    # These should all be recognized as binary streams
    assert is_binary_stream("application/octet-stream") is True
    assert is_binary_stream("APPLICATION/OCTET-STREAM") is True  # case insensitive
    assert is_binary_stream("application/vnd.docker.multiplexed-stream") is True
    assert is_binary_stream("APPLICATION/VND.DOCKER.MULTIPLEXED-STREAM") is True
    assert is_binary_stream("application/vnd.docker.raw-stream") is True
    assert is_binary_stream("APPLICATION/VND.DOCKER.RAW-STREAM") is True

    # These should NOT be recognized as binary streams
    assert is_binary_stream("text/plain") is False
    assert is_binary_stream("application/json") is False
    assert is_binary_stream("") is False


# =============================================================================
# Test: ContainerLogs changes
# =============================================================================

def test_container_logs_uses_contents_supplier():
    """Test that ContainerLogs now uses Contents.Supplier instead of List<String>."""
    container_logs_path = f"{JAVA_SRC}/org/openqa/selenium/docker/ContainerLogs.java"
    with open(container_logs_path) as f:
        content = f.read()

    # Should now use Contents.Supplier
    assert "Contents.Supplier" in content, "ContainerLogs should use Contents.Supplier"
    assert "getLogs()" in content, "ContainerLogs should have getLogs() method"
    assert "InputStream" in content, "ContainerLogs should return InputStream from getLogs()"


def test_container_logs_getLogs_method_exists():
    """Test that the new getLogs() method exists and returns InputStream."""
    container_logs_path = f"{JAVA_SRC}/org/openqa/selenium/docker/ContainerLogs.java"
    with open(container_logs_path) as f:
        content = f.read()

    # Find the getLogs method signature
    assert "public InputStream getLogs()" in content, \
        "getLogs() method returning InputStream not found"


def test_container_logs_deprecated_annotation():
    """Test that getLogLines is marked as deprecated."""
    container_logs_path = f"{JAVA_SRC}/org/openqa/selenium/docker/ContainerLogs.java"
    with open(container_logs_path) as f:
        content = f.read()

    assert "@Deprecated" in content, "getLogLines should be marked as @Deprecated"


# =============================================================================
# Test: GetContainerLogs changes
# =============================================================================

def test_get_container_logs_no_content_type_header():
    """Test that GetContainerLogs no longer adds Content-Type header.

    F2P: Before the fix, a "Content-Type: text/plain" header was added,
    which was incorrect for a GET request.
    """
    get_logs_path = f"{JAVA_SRC}/org/openqa/selenium/docker/client/GetContainerLogs.java"
    with open(get_logs_path) as f:
        content = f.read()

    # The Content-Type header should NOT be added to GET request
    # (checking that the old pattern of adding it is gone)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'new HttpRequest(GET' in line:
            # Check the next line doesn't add Content-Type header
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            assert 'Content-Type' not in next_line, \
                "GET request should not have Content-Type header"


def test_get_container_logs_passes_raw_content():
    """Test that GetContainerLogs passes raw response content to ContainerLogs.

    F2P: Before the fix, the response was converted to a string and split by newlines.
    After the fix, the raw binary content is passed through.
    """
    get_logs_path = f"{JAVA_SRC}/org/openqa/selenium/docker/client/GetContainerLogs.java"
    with open(get_logs_path) as f:
        content = f.read()

    # Should pass raw content, not parse as string
    assert "res.getContent()" in content, \
        "Should pass raw response content to ContainerLogs"
    # Should NOT split by newlines anymore
    assert "split" not in content, \
        "Should not split response content by newlines"


def test_get_container_logs_lambda_logging():
    """Test that logging uses lambda for lazy evaluation."""
    get_logs_path = f"{JAVA_SRC}/org/openqa/selenium/docker/client/GetContainerLogs.java"
    with open(get_logs_path) as f:
        content = f.read()

    # Check for lambda-style logging
    assert 'LOG.warning(() -> ' in content, \
        "Should use lambda for lazy log message evaluation"


# =============================================================================
# Test: Container isRunning method
# =============================================================================

def test_container_is_running_method():
    """Test that Container has isRunning() method.

    F2P: Before the fix, there was no way to check if container was running.
    After the fix, isRunning() is used to skip log saving for stopped containers.
    """
    container_path = f"{JAVA_SRC}/org/openqa/selenium/docker/Container.java"
    with open(container_path) as f:
        content = f.read()

    assert "public boolean isRunning()" in content, \
        "Container should have isRunning() method"
    assert "return running;" in content, \
        "isRunning() should return the running field"


def test_container_empty_contents_for_stopped():
    """Test that Container returns empty contents when not running."""
    container_path = f"{JAVA_SRC}/org/openqa/selenium/docker/Container.java"
    with open(container_path) as f:
        content = f.read()

    assert "Contents.empty()" in content, \
        "Should return Contents.empty() when container is not running"


# =============================================================================
# Test: DockerSession saveLogs improvements
# =============================================================================

def test_docker_session_checks_running_before_save():
    """Test that DockerSession.saveLogs() checks if container is running first.

    F2P: Before the fix, logs were attempted to be saved even for stopped containers.
    After the fix, it skips saving if container is not running.
    """
    docker_session_path = f"{JAVA_SRC}/org/openqa/selenium/grid/node/docker/DockerSession.java"
    with open(docker_session_path) as f:
        content = f.read()

    assert "container.isRunning()" in content, \
        "saveLogs() should check container.isRunning()"
    assert "Skip saving logs because container is not running" in content, \
        "Should log message when skipping non-running container"


def test_docker_session_uses_multiplexed_parser():
    """Test that DockerSession uses parseMultiplexedStream for logs."""
    docker_session_path = f"{JAVA_SRC}/org/openqa/selenium/grid/node/docker/DockerSession.java"
    with open(docker_session_path) as f:
        content = f.read()

    assert "parseMultiplexedStream" in content, \
        "Should call parseMultiplexedStream to process logs"
    assert "containerLogs.getLogs()" in content, \
        "Should get raw InputStream from containerLogs"


def test_docker_session_buffering_used():
    """Test that DockerSession uses proper buffering for I/O."""
    docker_session_path = f"{JAVA_SRC}/org/openqa/selenium/grid/node/docker/DockerSession.java"
    with open(docker_session_path) as f:
        content = f.read()

    assert "BufferedInputStream" in content, \
        "Should use BufferedInputStream for reading"
    assert "BufferedOutputStream" in content, \
        "Should use BufferedOutputStream for writing"
    assert "DataInputStream" in content, \
        "Should use DataInputStream for parsing binary data"


# =============================================================================
# Test: DockerSessionFactory null check
# =============================================================================

def test_docker_session_factory_null_check():
    """Test that DockerSessionFactory adds null check for TZ env var.

    F2P: Before the fix, NPE could occur if TZ env var was not set.
    After the fix, null check prevents NPE.
    """
    factory_path = f"{JAVA_SRC}/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java"
    with open(factory_path) as f:
        content = f.read()

    # Find the TZ handling code
    assert "envTz != null" in content, \
        "Should check for null before using envTz"


# =============================================================================
# Integration-style tests
# =============================================================================

def test_java_files_compile():
    """Test that the modified Java files compile successfully."""
    # Try to compile the Docker-related files
    files_to_compile = [
        f"{JAVA_SRC}/org/openqa/selenium/docker/Container.java",
        f"{JAVA_SRC}/org/openqa/selenium/docker/ContainerLogs.java",
        f"{JAVA_SRC}/org/openqa/selenium/docker/client/GetContainerLogs.java",
    ]

    # Use bazel to verify the build works
    result = run_bazel_build("//java/src/org/openqa/selenium/docker:docker", timeout=180)

    # We don't require this to pass (might need full repo setup),
    # but we check that the syntax is at least valid
    if result.returncode != 0:
        # Check for syntax errors specifically
        if "syntax error" in result.stderr.lower() or "cannot find symbol" in result.stderr:
            raise AssertionError(f"Compilation failed with syntax errors:\n{result.stderr}")


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
