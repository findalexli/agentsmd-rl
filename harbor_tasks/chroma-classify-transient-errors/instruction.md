# Classify Transient Errors for Retry in Chroma Log Service

## Problem

The Chroma log service and storage layer are not properly classifying transient errors, causing:
1. **gRPC transport errors** that should be retried (connection cancelled, closed, incomplete messages, timeouts) are being treated as non-retryable Cancelled errors
2. **GCS rate-limiting errors** (429 Too Many Requests, SlowDown, mutation rate limits) are being mapped to generic storage errors instead of backoff errors

This leads to unnecessary operation failures when transient network issues or rate limiting occurs, instead of properly retrying with backoff.

## Affected Files

- `rust/error/src/lib.rs` - Add utility for walking error source chains
- `rust/log/src/grpc_log.rs` - Classify retryable transport errors in gRPC status handling
- `rust/storage/src/object_storage.rs` - Detect GCS rate-limiting and map to Backoff errors

## Requirements

1. Add a `source_chain_contains` utility function that can walk an error's source chain and check if any error in the chain matches a predicate

2. For gRPC errors in `grpc_log.rs`:
   - Walk the error source chain on Cancelled gRPC status to detect underlying hyper transport errors (cancelled, closed, incomplete message, timeout)
   - Remap these transport-related Cancelled errors to Unavailable for retry
   - Plain Cancelled without transport errors should retain its original code
   - PushLogs should pass through the underlying error code instead of always returning Internal

3. For GCS errors in `object_storage.rs`:
   - Walk the error source chain on GCS Generic errors
   - Detect rate-limiting responses: 429 Too Many Requests, SlowDown code, mutation rate limit messages
   - Remap these to `StorageError::Backoff` instead of `StorageError::Generic`
   - Non-throttling errors (e.g., 503) should stay as Generic
   - Non-GCS stores (e.g., Azure) with 429 should stay as Generic

## Testing

All tests in the three modified crates should pass. Key test scenarios include:
- Error source chain traversal finds nested errors
- gRPC Unavailable stays Unavailable
- Plain gRPC Cancelled (without transport error) stays Cancelled
- GCS 429 errors trigger Backoff
- GCS SlowDown in source chain triggers Backoff
- Non-throttling GCS errors remain Generic
- Non-GCS 429 errors remain Generic
