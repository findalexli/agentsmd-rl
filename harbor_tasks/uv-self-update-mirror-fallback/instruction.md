# Bug: `uv self update` does not use the Astral mirror for version manifests

## Summary

When running `uv self update`, uv fetches the version manifest only from GitHub's raw content CDN. However, the `ruff` binary (also managed by uv) already fetches from the Astral releases mirror first and falls back to GitHub if that fails. The `uv` binary should follow the same pattern for consistency and resilience.

Additionally, there is a related resilience issue in the URL fallback logic. When fetching manifests, if a mirror returns a malformed response (such as corrupted data or encoding issues), the error recovery code does not recognize this as a reason to try alternative URLs. It should — a bad response from one source should not prevent trying another.

## Relevant Code

- `crates/uv-bin-install/src/lib.rs`
  - The `Binary` enum has a `manifest_urls` method that returns a list of URLs to try for each binary variant.
  - The `should_try_next_url` method on the `Error` type determines which errors trigger trying the next URL in the fallback chain.

## Expected Behavior

1. The `uv` binary variant in `manifest_urls` should try the same mirror endpoint that the `ruff` binary uses, before falling back to GitHub.
   - The URL list for `uv` should include the mirror URL first, then the canonical GitHub URL as a fallback.
   - The mirror URL is constructed using the `VERSIONS_MANIFEST_MIRROR` constant; the fallback uses `VERSIONS_MANIFEST_URL`.

2. Errors that indicate a malformed manifest response — specifically `ManifestParse` and `ManifestUtf8` variants — should trigger a fallback to alternative URLs. Currently, only `Download`, `ManifestFetch`, and `Stream` errors trigger fallback; parse and encoding errors do not.