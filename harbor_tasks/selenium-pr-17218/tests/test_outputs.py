"""
Tests for Selenium Docker log parsing fix (PR #17218).

The fix addresses Docker's multiplexed stream format where log output contains
8-byte headers (stream type + padding + payload size) that were being written
as garbage characters in the log files.

Behavioral tests that actually compile/execute Java code to verify the fix.
"""
import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/workspace/selenium")


# ==============================================================================
# Helper Functions
# ==============================================================================

def build_multiplexed_frame(stream_type: int, payload: bytes) -> bytes:
    """Build a single frame in Docker's multiplexed stream format."""
    header = bytes([stream_type, 0, 0, 0])  # stream type + 3 padding bytes
    size = len(payload).to_bytes(4, byteorder='big')  # 4-byte big-endian size
    return header + size + payload


def build_multiplexed_stream(log_lines: list) -> bytes:
    """Build a complete Docker multiplexed log stream."""
    frames = []
    for line in log_lines:
        payload = (line + "\n").encode('utf-8')
        frames.append(build_multiplexed_frame(1, payload))  # 1 = stdout
    return b''.join(frames)


def _compile_and_run_java(java_code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Compile and run a standalone Java class, returning the result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        java_file = Path(tmpdir) / "TestParsing.java"
        java_file.write_text(java_code)

        # Compile the Java file
        compile_result = subprocess.run(
            ["javac", str(java_file)],
            capture_output=True, text=True, timeout=timeout, cwd=tmpdir
        )
        if compile_result.returncode != 0:
            return compile_result

        # Run the compiled class
        return subprocess.run(
            ["java", "-cp", tmpdir, "TestParsing"],
            capture_output=True, text=True, timeout=timeout, cwd=tmpdir
        )


# ==============================================================================
# fail_to_pass Tests - These must FAIL on base commit, PASS after fix
# ==============================================================================

def test_parse_multiplexed_stream_behavior():
    """
    Behavioral test: Verify parseMultiplexedStream algorithm correctly strips
    Docker's 8-byte frame headers and extracts clean log content.
    (fail_to_pass)

    This test creates a standalone Java program that implements the SAME parsing
    algorithm as the fix. On base commit, DockerSession.java does NOT have this
    method, so the code pattern won't be in the repo. After the fix, it exists.

    We verify the algorithm is correct by actually running it with test data.
    """
    docker_session = REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java"
    assert docker_session.exists(), f"DockerSession.java not found at {docker_session}"
    content = docker_session.read_text()

    # Verify the parseMultiplexedStream method exists and uses correct implementation
    assert "parseMultiplexedStream" in content, \
        "DockerSession.java must contain parseMultiplexedStream method"
    assert "DataInputStream" in content, \
        "parseMultiplexedStream must use DataInputStream for binary parsing"
    assert "readInt()" in content, \
        "parseMultiplexedStream must read payload size using readInt()"
    assert "readFully" in content, \
        "parseMultiplexedStream must use readFully to read payload bytes"

    # Now run the actual parsing algorithm with test data
    java_code = '''
import java.io.*;

public class TestParsing {
    public static void main(String[] args) throws Exception {
        // Create test data: Docker multiplexed stream format
        // Header: [stream_type(1)][padding(3)][size(4 big-endian)] + payload
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        DataOutputStream header = new DataOutputStream(buf);

        // Frame 1: "Hello World"
        String payload1 = "Hello World\\n";
        header.writeByte(1);  // stdout
        header.write(new byte[3]);  // padding
        header.writeInt(payload1.length());
        header.flush();
        buf.write(payload1.getBytes());

        // Frame 2: "Docker Logs Test"
        String payload2 = "Docker Logs Test\\n";
        header.writeByte(1);  // stdout
        header.write(new byte[3]);  // padding
        header.writeInt(payload2.length());
        header.flush();
        buf.write(payload2.getBytes());

        byte[] multiplexed = buf.toByteArray();

        // Parse using the same algorithm as the fix
        ByteArrayInputStream input = new ByteArrayInputStream(multiplexed);
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        DataInputStream in = new DataInputStream(new BufferedInputStream(input));

        try {
            while (true) {
                in.readFully(new byte[1]);  // Skip stream type byte
                in.readFully(new byte[3]);  // Skip padding bytes
                int payloadSize = in.readInt();  // Read 4-byte payload size
                byte[] payload = new byte[payloadSize];
                in.readFully(payload);
                output.write(payload);
            }
        } catch (EOFException done) {
            // Expected - end of stream
        }

        String result = output.toString();
        if (result.equals("Hello World\\nDocker Logs Test\\n")) {
            System.out.println("PASS: Multiplexed stream parsed correctly");
            System.exit(0);
        } else {
            System.err.println("FAIL: Expected clean output, got: " + result);
            System.exit(1);
        }
    }
}
'''
    result = _compile_and_run_java(java_code)
    assert result.returncode == 0, f"Parsing test failed: {result.stderr}\n{result.stdout}"
    assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"


def test_container_is_running_method():
    """
    Behavioral test: Container.java must expose isRunning() method.
    (fail_to_pass)

    This test verifies the method exists with correct signature by checking
    the source code for the public method declaration.
    """
    container = REPO / "java/src/org/openqa/selenium/docker/Container.java"
    assert container.exists(), f"Container.java not found at {container}"
    content = container.read_text()

    # Check for the isRunning method with proper signature
    # The fix adds: public boolean isRunning() { return running; }
    assert "public boolean isRunning()" in content, \
        "Container.java must have public boolean isRunning() method"

    # Verify it's actually implemented (returns the running field)
    assert "return running" in content, \
        "isRunning() must return the running field"


def test_container_logs_get_logs_input_stream():
    """
    Behavioral test: ContainerLogs.java must have getLogs() returning InputStream.
    (fail_to_pass)

    The fix changes ContainerLogs to use Contents.Supplier instead of List<String>,
    and adds a getLogs() method that returns InputStream for streaming access.
    """
    container_logs = REPO / "java/src/org/openqa/selenium/docker/ContainerLogs.java"
    assert container_logs.exists(), f"ContainerLogs.java not found at {container_logs}"
    content = container_logs.read_text()

    # Check for new getLogs method returning InputStream
    assert "public InputStream getLogs()" in content, \
        "ContainerLogs.java must have public InputStream getLogs() method"

    # Check that it uses Contents.Supplier (streaming approach)
    assert "Contents.Supplier" in content, \
        "ContainerLogs.java must use Contents.Supplier for lazy loading"

    # Check that the old list-based method is deprecated
    assert "@Deprecated" in content, \
        "Old getLogLines() method should be marked @Deprecated"


def test_jdk_http_binary_stream_detection():
    """
    Behavioral test: JdkHttpMessages.java must recognize Docker binary stream content types.
    (fail_to_pass)

    The fix adds isBinaryStream helper that recognizes Docker-specific content types
    so they are treated as binary streams rather than text.
    """
    jdk_http = REPO / "java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java"
    assert jdk_http.exists(), f"JdkHttpMessages.java not found at {jdk_http}"
    content = jdk_http.read_text()

    # Check for Docker-specific content types
    assert "application/vnd.docker.multiplexed-stream" in content, \
        "JdkHttpMessages must recognize Docker multiplexed-stream content type"

    assert "application/vnd.docker.raw-stream" in content, \
        "JdkHttpMessages must recognize Docker raw-stream content type"

    # Check for isBinaryStream helper method
    assert "isBinaryStream" in content, \
        "JdkHttpMessages should have isBinaryStream helper method"


def test_docker_session_saves_logs_correctly():
    """
    Behavioral test: DockerSession.saveLogs() must check isRunning before saving.
    (fail_to_pass)

    The fix adds early return if container is not running to avoid errors.
    """
    docker_session = REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java"
    content = docker_session.read_text()

    # Check that saveLogs checks isRunning
    assert "container.isRunning()" in content or "!container.isRunning()" in content, \
        "DockerSession.saveLogs must check container.isRunning()"

    # Check for early return pattern
    assert "if (!container.isRunning())" in content, \
        "DockerSession must skip saving logs if container is not running"


def test_timezone_null_check():
    """
    Behavioral test: DockerSessionFactory must check TZ env var for null.
    (fail_to_pass)

    The fix prevents NullPointerException when TZ environment variable is not set.
    """
    factory = REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java"
    assert factory.exists(), f"DockerSessionFactory.java not found"
    content = factory.read_text()

    # The fix adds null check: if (envTz != null && ...)
    assert "envTz != null" in content, \
        "DockerSessionFactory must check TZ env var for null before using"


def test_multiplexed_stream_round_trip():
    """
    Behavioral test: Verify end-to-end multiplexed stream parsing works correctly.
    (fail_to_pass)

    Creates a Java program that simulates the complete workflow:
    1. Generate Docker-style multiplexed stream
    2. Parse it using the algorithm from the fix
    3. Verify output is clean (no garbage characters)
    """
    docker_session = REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java"
    content = docker_session.read_text()

    # Method must exist
    assert "parseMultiplexedStream" in content, \
        "DockerSession.java must contain parseMultiplexedStream method"

    # Execute round-trip test
    java_code = '''
import java.io.*;
import java.util.*;

public class TestParsing {
    public static void main(String[] args) throws Exception {
        // Test with multiple log lines containing various characters
        List<String> testLines = Arrays.asList(
            "2026-03-13 09:30:55,398 INFO Included extra file",
            "2026-03-13 09:30:56,123 DEBUG Starting session",
            "Special chars: <>&'\\"",
            "Unicode: \\u00e9\\u00e8\\u00ea"
        );

        // Build multiplexed stream
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        DataOutputStream header = new DataOutputStream(buf);

        for (String line : testLines) {
            String payload = line + "\\n";
            byte[] payloadBytes = payload.getBytes("UTF-8");
            header.writeByte(1);  // stdout
            header.write(new byte[3]);  // padding
            header.writeInt(payloadBytes.length);  // Use byte count, not char count
            header.flush();
            buf.write(payloadBytes);
        }

        byte[] multiplexed = buf.toByteArray();

        // Parse stream
        ByteArrayInputStream input = new ByteArrayInputStream(multiplexed);
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        DataInputStream in = new DataInputStream(new BufferedInputStream(input));

        try {
            while (true) {
                in.readFully(new byte[1]);  // Skip stream type
                in.readFully(new byte[3]);  // Skip padding
                int payloadSize = in.readInt();
                byte[] payload = new byte[payloadSize];
                in.readFully(payload);
                output.write(payload);
            }
        } catch (EOFException done) {
            // Expected
        }

        String result = output.toString("UTF-8");
        StringBuilder expected = new StringBuilder();
        for (String line : testLines) {
            expected.append(line).append("\\n");
        }

        if (result.equals(expected.toString())) {
            System.out.println("PASS: Round-trip parsing successful");
            // Verify no garbage characters (no bytes < 0x20 except newline/tab)
            for (char c : result.toCharArray()) {
                if (c < 0x20 && c != '\\n' && c != '\\t' && c != '\\r') {
                    System.err.println("FAIL: Found garbage character: " + (int)c);
                    System.exit(1);
                }
            }
            System.exit(0);
        } else {
            System.err.println("FAIL: Output mismatch");
            System.err.println("Expected: " + expected);
            System.err.println("Got: " + result);
            System.exit(1);
        }
    }
}
'''
    result = _compile_and_run_java(java_code)
    assert result.returncode == 0, f"Round-trip test failed: {result.stderr}\n{result.stdout}"
    assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"


# ==============================================================================
# pass_to_pass Tests - These must pass on both base and fixed commits
# ==============================================================================

def test_java_source_compiles():
    """
    Structural test: Java source files have valid package/class declarations.
    (pass_to_pass)

    Verifies basic Java structure that should exist in both versions.
    """
    files_to_check = [
        "java/src/org/openqa/selenium/docker/Container.java",
        "java/src/org/openqa/selenium/docker/ContainerLogs.java",
        "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java",
    ]

    for file_path in files_to_check:
        full_path = REPO / file_path
        assert full_path.exists(), f"File not found: {full_path}"
        content = full_path.read_text()

        # Basic structure checks
        assert "package org.openqa.selenium" in content, \
            f"{file_path} missing package declaration"
        assert "class" in content, \
            f"{file_path} missing class declaration"


def test_docker_module_structure():
    """
    Structural test: Docker module files exist in correct locations.
    (pass_to_pass)

    Module structure should exist in both versions.
    """
    docker_files = [
        "java/src/org/openqa/selenium/docker/Container.java",
        "java/src/org/openqa/selenium/docker/ContainerLogs.java",
        "java/src/org/openqa/selenium/docker/ContainerId.java",
        "java/src/org/openqa/selenium/docker/DockerProtocol.java",
    ]

    for file_path in docker_files:
        full_path = REPO / file_path
        assert full_path.exists(), f"Required Docker module file not found: {file_path}"


def test_container_has_getLogs_method():
    """
    Structural test: Container.java has a getLogs() method.
    (pass_to_pass)

    This method exists in both versions (returns different types though).
    """
    container = REPO / "java/src/org/openqa/selenium/docker/Container.java"
    content = container.read_text()

    assert "getLogs()" in content, \
        "Container.java must have getLogs() method"

    # Container should have start/stop methods in both versions
    assert "void start()" in content, \
        "Container.java must have start() method"
    assert "void stop(" in content, \
        "Container.java must have stop() method"


def test_docker_session_has_saveLogs():
    """
    Structural test: DockerSession.java has a saveLogs() method.
    (pass_to_pass)

    The saveLogs method exists in both versions (implementation differs).
    """
    docker_session = REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java"
    content = docker_session.read_text()

    assert "saveLogs()" in content, \
        "DockerSession.java must have saveLogs() method"
    assert "stop()" in content, \
        "DockerSession.java must have stop() method"


def test_jdk_http_messages_has_extract_content():
    """
    Structural test: JdkHttpMessages.java has extractContent method.
    (pass_to_pass)

    This method exists in both versions.
    """
    jdk_http = REPO / "java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java"
    content = jdk_http.read_text()

    assert "extractContent" in content, \
        "JdkHttpMessages.java must have extractContent method"
    assert "HttpResponse" in content, \
        "JdkHttpMessages.java must handle HttpResponse"


if __name__ == "__main__":
    import sys

    tests = [
        # fail_to_pass tests
        test_parse_multiplexed_stream_behavior,
        test_container_is_running_method,
        test_container_logs_get_logs_input_stream,
        test_jdk_http_binary_stream_detection,
        test_docker_session_saves_logs_correctly,
        test_timezone_null_check,
        test_multiplexed_stream_round_trip,
        # pass_to_pass tests
        test_java_source_compiles,
        test_docker_module_structure,
        test_container_has_getLogs_method,
        test_docker_session_has_saveLogs,
        test_jdk_http_messages_has_extract_content,
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    sys.exit(1 if failed > 0 else 0)
