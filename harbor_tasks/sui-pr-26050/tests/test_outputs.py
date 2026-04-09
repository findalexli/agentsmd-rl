"""Tests for sui-indexer-alt-framework checkpoint stream changes.

This module tests that:
1. CheckpointStream.stream is now Peekable<BoxStream> (not Pin<Box<dyn Stream>>)
2. GrpcStreamingClient::new() accepts statement_timeout parameter
3. wrap_stream function exists and applies timeout correctly
4. MockStreamingClient uses the new wrap_stream pattern
5. The crate compiles
"""

import subprocess
import re

REPO = "/workspace/sui"
CRATE_PATH = f"{REPO}/crates/sui-indexer-alt-framework"
STREAMING_CLIENT = f"{CRATE_PATH}/src/ingestion/streaming_client.rs"
MOD_RS = f"{CRATE_PATH}/src/ingestion/mod.rs"
BROADCASTER = f"{CRATE_PATH}/src/ingestion/broadcaster.rs"


def test_cargo_check():
    """Verify the crate compiles successfully (pass_to_pass).

    This ensures the code changes don't break compilation.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_rustfmt_check():
    """Verify the crate's Rust files are properly formatted (pass_to_pass).

    This ensures the code follows the project's formatting standards.
    """
    result = subprocess.run(
        ["cargo", "fmt", "-p", "sui-indexer-alt-framework", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"rustfmt check failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_crate_structure():
    """Verify the crate has the expected module structure (pass_to_pass).

    This ensures all required source files and modules are present.
    """
    import os

    expected_files = [
        f"{CRATE_PATH}/Cargo.toml",
        f"{CRATE_PATH}/src/lib.rs",
        f"{CRATE_PATH}/src/config.rs",
        f"{CRATE_PATH}/src/metrics.rs",
        f"{CRATE_PATH}/src/ingestion/mod.rs",
        f"{CRATE_PATH}/src/ingestion/broadcaster.rs",
        f"{CRATE_PATH}/src/ingestion/streaming_client.rs",
        f"{CRATE_PATH}/src/ingestion/ingestion_client.rs",
        f"{CRATE_PATH}/src/ingestion/error.rs",
        f"{CRATE_PATH}/src/pipeline/mod.rs",
    ]

    for file_path in expected_files:
        assert os.path.isfile(file_path), f"Required file missing: {file_path}"


def test_ingestion_module_exports():
    """Verify ingestion module exports key types (pass_to_pass).

    This ensures the public API surface is intact.
    """
    with open(f"{CRATE_PATH}/src/ingestion/mod.rs", "r") as f:
        content = f.read()

    # Check that key types are publicly accessible
    assert "pub struct IngestionService" in content, "IngestionService should be public"
    assert "pub fn subscribe" in content, "subscribe method should exist"
    assert "pub struct IngestionConfig" in content, "IngestionConfig should be public"


def test_checkpoint_stream_peekable_type():
    """CheckpointStream.stream must be Peekable<BoxStream> (fail_to_pass).

    Before: stream: Pin<Box<dyn Stream<Item = Result<Checkpoint>> + Send>>
    After: stream: Peekable<BoxStream<'static, Result<Checkpoint>>>
    """
    with open(STREAMING_CLIENT, "r") as f:
        content = f.read()

    # Should have the new Peekable<BoxStream> type
    assert "Peekable<BoxStream<'static, Result<Checkpoint>>>" in content, \
        "CheckpointStream.stream should be Peekable<BoxStream<'static, Result<Checkpoint>>>"

    # Should NOT have the old Pin<Box<dyn Stream>> type
    old_pattern = r"Pin<Box<dyn Stream<Item\s*=\s*Result<Checkpoint>>\s*\+\s*Send>>"
    assert not re.search(old_pattern, content), \
        "CheckpointStream.stream should NOT use old Pin<Box<dyn Stream>> type"


def test_grpc_streaming_client_has_statement_timeout():
    """GrpcStreamingClient must store and use statement_timeout (fail_to_pass).

    The struct should have a statement_timeout field and new() should accept it.
    """
    with open(STREAMING_CLIENT, "r") as f:
        content = f.read()

    # Check struct has statement_timeout field
    assert "statement_timeout: Duration" in content, \
        "GrpcStreamingClient must have statement_timeout field"

    # Check new() accepts statement_timeout parameter
    new_sig_pattern = r"pub fn new\([^)]*statement_timeout:\s*Duration[^)]*\)"
    assert re.search(new_sig_pattern, content), \
        "GrpcStreamingClient::new() must accept statement_timeout parameter"


def test_wrap_stream_function_exists():
    """wrap_stream function must exist to wrap streams with timeout (fail_to_pass).

    This function wraps a stream with per-item timeout and makes it peekable.
    """
    with open(STREAMING_CLIENT, "r") as f:
        content = f.read()

    # Check wrap_stream function exists
    assert "fn wrap_stream(" in content, \
        "wrap_stream function must be defined"

    # Check it returns Peekable<BoxStream>
    wrap_sig_pattern = r"fn wrap_stream\([^)]*\)\s*->\s*Peekable<BoxStream<'static,\s*Result<Checkpoint>>>"
    assert re.search(wrap_sig_pattern, content), \
        "wrap_stream must return Peekable<BoxStream<'static, Result<Checkpoint>>>"

    # Check it uses tokio_stream::StreamExt::timeout or StreamExt::timeout
    assert "StreamExt::timeout" in content, \
        "wrap_stream should use StreamExt::timeout for statement timeout"

    # Check it makes the stream peekable
    assert ".peekable()" in content, \
        "wrap_stream should call .peekable() on the stream"


def test_broadcaster_uses_peekable_stream():
    """Broadcaster must use the peekable stream from client directly (fail_to_pass).

    Before: broadcaster wrapped the stream with timeout locally
    After: broadcaster uses stream.peekable() from client directly
    """
    with open(BROADCASTER, "r") as f:
        content = f.read()

    # Check it uses Pin::new(&mut stream).peek()
    assert "Pin::new(&mut stream).peek()" in content, \
        "Broadcaster should use Pin::new(&mut stream).peek() on the peekable stream"

    # Should NOT have the old pattern of wrapping with timeout locally
    old_timeout_pattern = r"\.timeout\(config\.streaming_statement_timeout\(\)\)"
    assert not re.search(old_timeout_pattern, content), \
        "Broadcaster should NOT wrap stream with timeout locally (now done in client)"

    # Check it uses map_ok for envelope conversion
    assert "stream.map_ok" in content, \
        "Broadcaster should use stream.map_ok for CheckpointEnvelope conversion"


def test_mod_rs_passes_statement_timeout():
    """mod.rs must pass statement_timeout to GrpcStreamingClient::new() (fail_to_pass)."""
    with open(MOD_RS, "r") as f:
        content = f.read()

    # Check that GrpcStreamingClient::new is called with 3 arguments including statement_timeout
    new_call_pattern = r"GrpcStreamingClient::new\(\s*[^,]+,\s*[^,]+,\s*config\.streaming_statement_timeout\(\)"
    assert re.search(new_call_pattern, content), \
        "mod.rs must call GrpcStreamingClient::new(uri, connection_timeout, statement_timeout)"


def test_mock_streaming_client_uses_wrap_stream():
    """MockStreamingClient must use wrap_stream for consistent behavior (fail_to_pass)."""
    with open(STREAMING_CLIENT, "r") as f:
        content = f.read()

    # Find the test_utils module and check MockStreamingClient
    # Check that connect() returns stream wrapped with wrap_stream
    assert "wrap_stream(stream_state, self.statement_timeout)" in content, \
        "MockStreamingClient::connect() must use wrap_stream() for consistent behavior"

    # Check MockStreamingClient has statement_timeout field
    assert "statement_timeout: Duration," in content, \
        "MockStreamingClient must have statement_timeout field"
