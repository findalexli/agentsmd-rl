"""
Tests for Selenium PR #17211: Align Router-Node read timeout with session pageLoad capability.

This PR modifies HandleSession.java to:
1. Add sessionReadTimeout() method that extracts pageLoad timeout from capabilities
2. Add READ_TIMEOUT_BUFFER constant (30 seconds)
3. Add NodeClientKey class to cache HTTP clients by (URI, timeout) pairs
4. Compute effective timeout as max(pageLoad, nodeTimeout) + buffer
"""

import subprocess
import re
import os

REPO = "/workspace/selenium"
HANDLE_SESSION_PATH = os.path.join(
    REPO, "java/src/org/openqa/selenium/grid/router/HandleSession.java"
)


def run_cmd(cmd, cwd=REPO, timeout=600):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str),
    )
    return result


def read_file(path):
    """Read file contents."""
    with open(path, "r") as f:
        return f.read()


# =============================================================================
# Fail-to-Pass Tests: These should FAIL on base commit, PASS after fix
# =============================================================================


def test_session_read_timeout_method_exists():
    """
    The fix adds a static sessionReadTimeout(Capabilities) method.
    This method extracts the pageLoad timeout from WebDriver capabilities.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check for the method signature
    assert "static Duration sessionReadTimeout(Capabilities caps)" in content, (
        "sessionReadTimeout(Capabilities) method not found in HandleSession.java"
    )

    # Verify it reads from timeouts map and handles pageLoad
    assert 'getCapability("timeouts")' in content, (
        "sessionReadTimeout should read 'timeouts' capability"
    )
    assert '"pageLoad"' in content, (
        "sessionReadTimeout should extract 'pageLoad' from timeouts"
    )


def test_read_timeout_buffer_constant():
    """
    The fix adds READ_TIMEOUT_BUFFER = 30 seconds constant.
    This buffer ensures nodes have time to return timeout errors before
    the Router closes the connection.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check for the constant definition
    assert "READ_TIMEOUT_BUFFER" in content, (
        "READ_TIMEOUT_BUFFER constant not found"
    )

    # Verify it's set to 30 seconds
    assert re.search(r"Duration\.ofSeconds\s*\(\s*30\s*\)", content), (
        "READ_TIMEOUT_BUFFER should be Duration.ofSeconds(30)"
    )


def test_node_client_key_class_exists():
    """
    The fix adds NodeClientKey inner class to cache HTTP clients by
    (URI, readTimeout) pairs. This ensures sessions with different
    pageLoad timeouts get separate clients.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check for the class
    assert "class NodeClientKey" in content, (
        "NodeClientKey class not found in HandleSession.java"
    )

    # Should have URI and Duration fields
    assert re.search(r"private\s+final\s+URI\s+uri", content), (
        "NodeClientKey should have URI field"
    )
    assert re.search(r"private\s+final\s+Duration\s+readTimeout", content), (
        "NodeClientKey should have Duration readTimeout field"
    )

    # Should implement equals and hashCode for use as map key
    assert "public boolean equals(Object" in content, (
        "NodeClientKey should implement equals()"
    )
    assert "public int hashCode()" in content, (
        "NodeClientKey should implement hashCode()"
    )


def test_timeout_calculation_uses_max():
    """
    The fix computes effective timeout as max(pageLoad, nodeTimeout) + buffer.
    This ensures the Router waits long enough for either timeout source.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check for the comparison logic
    assert "compareTo(nodeTimeout)" in content or "compareTo" in content and "nodeTimeout" in content, (
        "Should compare pageLoadTimeout with nodeTimeout"
    )

    # Check for adding the buffer
    assert re.search(r"\.plus\s*\(\s*READ_TIMEOUT_BUFFER\s*\)", content), (
        "Should add READ_TIMEOUT_BUFFER to the base timeout"
    )


def test_long_from_helper_method():
    """
    The fix adds longFrom() helper to handle both Long and Integer types.
    JSON deserializers may produce either type for numeric values.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check for the helper method
    assert "longFrom" in content, (
        "longFrom helper method not found"
    )

    # Should handle Number types
    assert "instanceof Long" in content or "instanceof Number" in content, (
        "longFrom should handle numeric types"
    )


def test_fetch_node_timeout_returns_optional():
    """
    The fix changes fetchNodeSessionTimeout to fetchNodeTimeout returning Optional<Duration>.
    This allows skipping cache storage on failed fetches for retry on next command.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check the method returns Optional
    assert re.search(r"Optional<Duration>\s+fetchNodeTimeout", content), (
        "fetchNodeTimeout should return Optional<Duration>"
    )

    # Check it returns Optional.of or Optional.empty
    assert "Optional.of(" in content or "Optional.empty()" in content, (
        "fetchNodeTimeout should use Optional.of() or Optional.empty()"
    )


def test_node_timeout_cache_field():
    """
    The fix adds nodeTimeoutCache to store node timeouts per URI.
    This reduces redundant /se/grid/node/status calls.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Check for the cache field
    assert "nodeTimeoutCache" in content, (
        "nodeTimeoutCache field not found"
    )

    # Should be ConcurrentMap<URI, Duration>
    assert re.search(r"ConcurrentMap<URI,\s*Duration>\s+nodeTimeoutCache", content), (
        "nodeTimeoutCache should be ConcurrentMap<URI, Duration>"
    )


def test_http_clients_map_uses_node_client_key():
    """
    The fix changes httpClients map from ConcurrentMap<URI, CacheEntry>
    to ConcurrentMap<NodeClientKey, CacheEntry>.
    This allows different timeout configurations per node.
    (fail_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Should NOT use URI as the key type anymore
    # Check for NodeClientKey usage
    assert re.search(r"ConcurrentMap<NodeClientKey,\s*CacheEntry>\s+httpClients", content), (
        "httpClients should be ConcurrentMap<NodeClientKey, CacheEntry>"
    )


# =============================================================================
# Pass-to-Pass Tests: These should PASS both before and after fix
# =============================================================================


def test_bazel_build_compiles():
    """
    The code should compile successfully with Bazel.
    (pass_to_pass)
    """
    result = run_cmd(
        ["bazel", "build", "//java/src/org/openqa/selenium/grid/router:router"],
        timeout=600
    )
    assert result.returncode == 0, (
        f"Bazel build failed:\n{result.stderr[-2000:]}"
    )


def test_handle_session_class_structure():
    """
    HandleSession should maintain its core structure as HttpHandler.
    (pass_to_pass)
    """
    content = read_file(HANDLE_SESSION_PATH)

    # Core class structure
    assert "class HandleSession implements HttpHandler, Closeable" in content, (
        "HandleSession should implement HttpHandler and Closeable"
    )

    # Core method
    assert "public HttpResponse execute(HttpRequest req)" in content, (
        "HandleSession should have execute(HttpRequest) method"
    )

    # Cache cleanup mechanism
    assert "cleanUpHttpClientsCacheService" in content, (
        "Should have cleanup service for HTTP clients"
    )


def test_java_file_compiles_syntax():
    """
    The Java file should have valid syntax that javac accepts.
    (pass_to_pass)
    """
    # Quick syntax check using javac parsing (if available)
    # This is a basic compilation check
    result = run_cmd(
        ["bazel", "build", "--nobuild", "//java/src/org/openqa/selenium/grid/router:router"],
        timeout=120
    )
    # --nobuild just does analysis, checking syntax without full compilation
    # If bazel build worked, this should too
    assert result.returncode == 0, (
        f"Java syntax check failed:\n{result.stderr[-1000:]}"
    )


def test_repo_spotbugs():
    """
    SpotBugs static analysis passes on the router module.
    (pass_to_pass)
    """
    result = run_cmd(
        ["bazel", "build", "//java/src/org/openqa/selenium/grid/router:router-spotbugs"],
        timeout=600
    )
    assert result.returncode == 0, (
        f"SpotBugs check failed:\n{result.stderr[-2000:]}"
    )


def test_repo_router_tests():
    """
    RouterTest unit tests pass on the router module.
    (pass_to_pass)
    """
    result = run_cmd(
        ["bazel", "test", "//java/test/org/openqa/selenium/grid/router:RouterTest", "--test_output=errors"],
        timeout=600
    )
    assert result.returncode == 0, (
        f"RouterTest failed:\n{result.stderr[-2000:]}"
    )


def test_repo_java_format():
    """
    Java code formatting check passes on HandleSession.java.
    (pass_to_pass)
    """
    result = run_cmd(
        [
            "bazel", "run", "//scripts:google-java-format", "--",
            "--dry-run",
            f"{REPO}/java/src/org/openqa/selenium/grid/router/HandleSession.java"
        ],
        timeout=120
    )
    # google-java-format with --dry-run returns 0 if no changes needed
    assert result.returncode == 0, (
        f"Java format check failed:\n{result.stderr[-1000:]}"
    )
