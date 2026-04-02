# Bug: Direct URL wheel streaming failures not caught for fallback download

## Summary

When installing a wheel from a direct URL, `uv` attempts to stream the wheel for extraction. If streaming is **unsupported** (e.g., server doesn't support range requests), it's supposed to fall back to downloading the entire wheel to disk first.

However, there is a bug in the error handling in `crates/uv-distribution/src/distribution_database.rs`: the fallback path for `BuiltDist::DirectUrl` wheels matches the wrong error variant. The streaming result is wrapped in an extraction error, but the match arm catches a different error type — so the fallback never triggers.

Additionally, streaming can also **fail** mid-stream (e.g., connection reset during extraction), and this case has no fallback handling at all. When streaming fails partway through, the error propagates as a hard failure instead of retrying with a full download.

## Where to look

- `crates/uv-distribution/src/distribution_database.rs` — the `get_or_build_wheel` method, specifically the `BuiltDist::DirectUrl` match arm
- Look at how the first `BuiltDist::Registry` arm (earlier in the same function) handles streaming errors — it correctly catches the right error variant and handles both "unsupported" and "failed" cases
- `crates/uv-extract/src/error.rs` — defines the methods for checking streaming error types

## Expected behavior

When streaming a direct URL wheel fails or is unsupported, `uv` should log a warning and fall back to downloading the wheel directly to disk, the same way it already does for registry wheels.

## Actual behavior

Streaming failures for direct URL wheels propagate as hard errors because the error variant matching is wrong — the code will never enter the fallback branch.
