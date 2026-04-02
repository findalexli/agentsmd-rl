# Bug: `uv self update` does not use the Astral mirror for version manifests

## Summary

When running `uv self update`, uv fetches the version manifest only from GitHub's raw content CDN. However, the `ruff` binary (also managed by uv) already fetches from the Astral releases mirror first and falls back to GitHub if that fails. The `uv` binary should follow the same pattern for consistency and resilience.

Additionally, there is a related resilience issue in the URL fallback logic. When fetching manifests, if a mirror returns a malformed response (corrupted data, encoding issues), the error recovery code does not recognize this as a reason to try alternative URLs. It should — a bad response from one source should not prevent trying another.

## Relevant Code

- `crates/uv-bin-install/src/lib.rs`
  - Look at how different binaries configure their manifest URL lists. Compare how `Ruff` and `Uv` are handled differently.
  - Look at the `RetriableError` implementation — specifically how it decides which errors should trigger trying the next URL. Not all manifest-related error variants are covered.

## Expected Behavior

1. `uv self update` should try the same mirror endpoint that `ruff` uses, before falling back to GitHub.
2. All manifest-related errors (not just network failures) should trigger a fallback to alternative URLs.
