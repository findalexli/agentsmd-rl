# Task: Make CheckpointStream Peekable and Centralize Timeout Handling

## Problem

The `CheckpointStream` struct in `crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs` currently wraps its stream in a way that makes it difficult to peek at the next checkpoint without consuming it. Additionally, the statement timeout logic is currently implemented in the broadcaster, which means other users of the streaming client cannot benefit from consistent timeout handling.

## Goal

Refactor the streaming infrastructure to:

1. Make `CheckpointStream.stream` peekable so callers can inspect the next checkpoint without consuming it
2. Move the per-item statement timeout logic into `GrpcStreamingClient` so all stream users get consistent timeout behavior
3. Update `MockStreamingClient` to use the same timeout wrapping for test consistency

## Files to Modify

- `crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs` - Main changes to `CheckpointStream`, `GrpcStreamingClient`, and `MockStreamingClient`
- `crates/sui-indexer-alt-framework/src/ingestion/mod.rs` - Update `GrpcStreamingClient::new()` call to pass the statement timeout
- `crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs` - Simplify to use the peekable stream directly from the client

## Key Requirements

1. `CheckpointStream.stream` should be `Peekable<BoxStream<'static, Result<Checkpoint>>>` instead of `Pin<Box<dyn Stream>>`
2. `GrpcStreamingClient` should accept and store a `statement_timeout: Duration` parameter
3. A new `wrap_stream()` function should apply the timeout and make streams peekable
4. The broadcaster should use `Pin::new(&mut stream).peek()` directly without local timeout wrapping
5. All existing tests should continue to pass

## Relevant Types

- `CheckpointStream` - Container for the stream and chain ID
- `GrpcStreamingClient` - Real gRPC streaming client
- `MockStreamingClient` - Test mock for streaming
- `Checkpoint` - The item being streamed
- `CheckpointEnvelope` - Wrapper used by the broadcaster

## Testing

Run `cargo check -p sui-indexer-alt-framework` and `cargo test -p sui-indexer-alt-framework --lib` to verify your changes.
