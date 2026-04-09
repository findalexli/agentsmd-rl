# Remove Backwards Compatibility for Non-TLS Connections

The validator server currently supports a deprecated `allow_insecure` mode that allows clients to connect without TLS even when the server is configured with TLS. This backwards compatibility needs to be removed in favor of mandatory TLS connections.

## Problem

The `sui-http` crate has an `allow_insecure` configuration option in `Config` struct (in `crates/sui-http/src/config.rs`) that, when enabled, allows the server to accept both TLS and non-TLS connections on the same port. This is done by peeking at the first byte of incoming connections to detect TLS handshakes (0x16). This behavior is a security risk and needs to be removed.

The `sui-network` validator server in `crates/sui-network/src/validator/server.rs` currently enables this insecure mode with `.allow_insecure(true)`.

## What You Need to Do

1. **Remove `allow_insecure` from `Config` struct** (`crates/sui-http/src/config.rs`):
   - Remove the `allow_insecure: bool` field
   - Add two new fields:
     - `tls_handshake_timeout: Duration` - timeout for TLS handshakes (default: 5 seconds)
     - `max_pending_connections: usize` - maximum pending TLS handshakes (default: 4096)
   - Add constants for these defaults: `DEFAULT_TLS_HANDSHAKE_TIMEOUT` and `DEFAULT_MAX_PENDING_CONNECTIONS`
   - Replace the `allow_insecure()` builder method with `tls_handshake_timeout()` and `max_pending_connections()` methods
   - Update the `Default` impl to use the new fields

2. **Update TLS handling** (`crates/sui-http/src/lib.rs`):
   - Remove all insecure connection handling logic including:
     - The `allow_insecure` check
     - The `std::any::Any` downcast to `tokio::net::TcpStream`
     - The 1-byte peek to detect TLS (0x16 check)
     - The "accepting insecure connection" path
   - Add check for `max_pending_connections` before spawning TLS handshake tasks - drop new connections with a warning log when limit reached
   - Wrap the TLS acceptor in `tokio::time::timeout()` using `tls_handshake_timeout` - map timeout to an io::Error with message "TLS handshake timed out"

3. **Update accept error handling** (`crates/sui-http/src/listener.rs`):
   - Reduce the sleep duration in `handle_accept_error` from 1 second to 5 milliseconds
   - Update the comment to explain why we sleep briefly

4. **Remove allow_insecure from validator** (`crates/sui-network/src/validator/server.rs`):
   - Remove the `.allow_insecure(true)` call on http_config
   - Use `self.config.http_config()` directly when building the server

## Files to Modify

- `crates/sui-http/src/config.rs` - Config struct and builder methods
- `crates/sui-http/src/lib.rs` - TLS handling logic
- `crates/sui-http/src/listener.rs` - Accept error sleep duration
- `crates/sui-network/src/validator/server.rs` - Remove allow_insecure usage

## Verification

After your changes:
- The code should compile with `cargo check -p sui-http` and `cargo check -p sui-network`
- There should be no references to `allow_insecure` in any of the modified files
- The TLS handshake should be wrapped in a timeout
- New connections should be dropped when max_pending_connections is reached
