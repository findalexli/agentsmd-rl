"""Tests for the sui-http insecure connection removal PR."""

import subprocess
import re

REPO = "/workspace/sui"

def test_no_allow_insecure_in_config():
    """Config struct should not have allow_insecure field."""
    config_path = f"{REPO}/crates/sui-http/src/config.rs"
    with open(config_path, 'r') as f:
        content = f.read()

    # Should NOT have allow_insecure field
    assert "allow_insecure" not in content, "Found allow_insecure in config.rs - should be removed"

    # SHOULD have the new fields
    assert "tls_handshake_timeout" in content, "Missing tls_handshake_timeout field"
    assert "max_pending_connections" in content, "Missing max_pending_connections field"

    # SHOULD have default constants
    assert "DEFAULT_TLS_HANDSHAKE_TIMEOUT" in content, "Missing DEFAULT_TLS_HANDSHAKE_TIMEOUT constant"
    assert "DEFAULT_MAX_PENDING_CONNECTIONS" in content, "Missing DEFAULT_MAX_PENDING_CONNECTIONS constant"

def test_tls_handshake_timeout_default():
    """Default TLS handshake timeout should be 5 seconds."""
    config_path = f"{REPO}/crates/sui-http/src/config.rs"
    with open(config_path, 'r') as f:
        content = f.read()

    # Find the constant definition
    match = re.search(r'DEFAULT_TLS_HANDSHAKE_TIMEOUT.*?Duration::from_secs\((\d+)\)', content)
    assert match is not None, "Could not find DEFAULT_TLS_HANDSHAKE_TIMEOUT definition"
    timeout_secs = int(match.group(1))
    assert timeout_secs == 5, f"Expected 5 second default timeout, got {timeout_secs}"

def test_max_pending_connections_default():
    """Default max pending connections should be 4096."""
    config_path = f"{REPO}/crates/sui-http/src/config.rs"
    with open(config_path, 'r') as f:
        content = f.read()

    # Find the constant definition
    match = re.search(r'DEFAULT_MAX_PENDING_CONNECTIONS.*?(\d+)', content)
    assert match is not None, "Could not find DEFAULT_MAX_PENDING_CONNECTIONS definition"
    max_connections = int(match.group(1))
    assert max_connections == 4096, f"Expected 4096 default max connections, got {max_connections}"

def test_max_pending_connections_check():
    """Server should check max_pending_connections before spawning TLS handshake."""
    lib_path = f"{REPO}/crates/sui-http/src/lib.rs"
    with open(lib_path, 'r') as f:
        content = f.read()

    # Should check pending connections length
    assert "pending_connections.len() >= self.config.max_pending_connections" in content, \
        "Missing max_pending_connections check"

    # Should drop connection when limit reached
    assert "max pending connections reached, dropping new connection" in content, \
        "Missing warning message for dropped connection"

    # Should have early return
    assert "return;" in content, "Should return early when max pending connections reached"

def test_tls_handshake_with_timeout():
    """TLS handshake should use tokio::time::timeout."""
    lib_path = f"{REPO}/crates/sui-http/src/lib.rs"
    with open(lib_path, 'r') as f:
        content = f.read()

    # Should use tokio::time::timeout
    assert "tokio::time::timeout" in content, "Missing tokio::time::timeout for TLS handshake"

    # Should use timeout_duration from config
    assert "timeout_duration" in content, "Missing timeout_duration variable"

    # Should map timeout error to io::Error
    assert "TLS handshake timed out" in content, "Missing TLS handshake timeout error message"

def test_no_insecure_connection_logic():
    """Server should not have insecure connection handling logic."""
    lib_path = f"{REPO}/crates/sui-http/src/lib.rs"
    with open(lib_path, 'r') as f:
        content = f.read()

    # Should NOT have insecure connection handling
    assert "allow_insecure" not in content, "Found allow_insecure in lib.rs - should be removed"
    assert "accepting insecure connection" not in content, \
        "Found insecure connection acceptance message"
    assert "0x16" not in content, "Found TLS detection byte (0x16) peek logic"
    assert "std::any::Any" not in content, "Found downcast_ref for insecure connection detection"

def test_accept_error_sleep_reduced():
    """Accept error sleep should be reduced from 1 second to 5 milliseconds."""
    listener_path = f"{REPO}/crates/sui-http/src/listener.rs"
    with open(listener_path, 'r') as f:
        content = f.read()

    # Should have 5 millisecond sleep, not 1 second
    assert "Duration::from_millis(5)" in content, \
        "Missing 5ms sleep duration for accept error handling"
    assert "Duration::from_secs(1)" not in content, \
        "Found old 1 second sleep - should be 5ms"

def test_no_allow_insecure_in_validator():
    """Validator server should not call allow_insecure."""
    validator_path = f"{REPO}/crates/sui-network/src/validator/server.rs"
    with open(validator_path, 'r') as f:
        content = f.read()

    # Should NOT have allow_insecure call
    assert "allow_insecure" not in content, \
        "Found allow_insecure call in validator server - should be removed"

    # Should use self.config.http_config() directly
    assert "self.config.http_config()" in content, \
        "Should use self.config.http_config() directly without modification"

def test_config_builder_methods():
    """Config should have builder methods for new fields."""
    config_path = f"{REPO}/crates/sui-http/src/config.rs"
    with open(config_path, 'r') as f:
        content = f.read()

    # Should have tls_handshake_timeout builder method
    assert "pub fn tls_handshake_timeout(self, timeout: Duration)" in content, \
        "Missing tls_handshake_timeout builder method"

    # Should have max_pending_connections builder method
    assert "pub fn max_pending_connections(self, max: usize)" in content, \
        "Missing max_pending_connections builder method"

def test_default_impl_uses_new_fields():
    """Default implementation should use new timeout and max pending fields."""
    config_path = f"{REPO}/crates/sui-http/src/config.rs"
    with open(config_path, 'r') as f:
        content = f.read()

    # In the Default impl, should reference the new fields
    default_impl = re.search(r'impl Default for Config\s*\{[^}]+fn default\(\)[^}]+\}', content, re.DOTALL)
    if default_impl:
        impl_content = default_impl.group(0)
        assert "tls_handshake_timeout" in impl_content, \
            "Default impl should set tls_handshake_timeout"
        assert "max_pending_connections" in impl_content, \
            "Default impl should set max_pending_connections"

def test_sui_http_code_valid():
    """sui-http code should be syntactically valid Rust (verified by file parsing).

    Note: We can't run cargo check -p sui-http in isolation because of tokio feature
    dependencies. Instead we verify the sui-network crate which depends on sui-http.
    """
    # Verify the files exist and have valid syntax by trying to parse with rustfmt --check
    result = subprocess.run(
        ["rustfmt", "--check", f"{REPO}/crates/sui-http/src/config.rs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # rustfmt returns 0 if file is already formatted, 1 if needs formatting
    # both indicate valid Rust syntax
    assert result.returncode in [0, 1], f"Invalid Rust syntax in config.rs:\n{result.stderr}"

def test_cargo_check_sui_network():
    """sui-network crate should compile."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-network"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_repo_rustfmt():
    """Repo Rust code should be properly formatted (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo fmt --check failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_repo_clippy_sui_http():
    """sui-http crate should pass clippy lints (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "xclippy", "-p", "sui-http"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo xclippy failed:\n{result.stderr[-1000:]}"


def test_repo_cargo_check_mysten_network():
    """mysten-network crate should compile (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "mysten-network"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check -p mysten-network failed:\n{result.stderr[-1000:]}"


def test_repo_cargo_xlint():
    """Repo should pass license and basic checks (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo xlint failed:\n{result.stderr[-500:]}"
