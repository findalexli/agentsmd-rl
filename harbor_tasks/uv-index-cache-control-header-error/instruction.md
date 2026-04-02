# Invalid cache-control header values cause runtime panic

## Bug Description

When a user configures a custom `cache-control` header for a package index in their `pyproject.toml` (e.g., under `[[tool.uv.index]]`), invalid HTTP header values — such as those containing newlines or other control characters — are accepted during configuration parsing but cause a **panic at runtime** when the value is actually used in an HTTP request.

The panic comes from an `.expect()` call when converting the stored string to an HTTP `HeaderValue`. For example, a configuration like:

```toml
[[tool.uv.index]]
name = "my-index"
url = "https://example.com/simple"
cache-control.api = """
max-age=600
"""
```

...will be parsed without error but will panic when uv tries to make a request using that cache-control value.

## Relevant Files

- `crates/uv-distribution-types/src/index.rs` — The `IndexCacheControl` struct and its `Serialize`/`Deserialize` implementation. Cache control values are currently stored as `SmallString` and only validated later.
- `crates/uv-client/src/cached_client.rs` — The `CacheControl` enum and the `send_cached` / `fresh_request` methods where cache-control values are converted to HTTP headers.
- `crates/uv-distribution-types/src/index_url.rs` — Functions that look up cache-control headers for index URLs.

## Expected Behavior

Invalid cache-control values should be rejected **during configuration parsing** (deserialization) with a clear, user-facing error message — not cause a panic at runtime.

## Hints

- Consider validating the header value at deserialization time rather than at usage time.
- The `http::HeaderValue` type from the `http` crate provides the validation you need.
- Think about what type should be stored in `IndexCacheControl` fields to guarantee validity.
