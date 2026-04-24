# Bug: `uv self update` does not use the Astral mirror for version manifests

## Summary

When running `uv self update`, uv fetches the version manifest only from GitHub's raw content CDN. However, the `ruff` binary (also managed by uv) already fetches from the Astral releases mirror first and falls back to GitHub if that fails. The `uv` binary should follow the same pattern for consistency and resilience.

Additionally, there is a related resilience issue in the URL fallback logic. When fetching manifests, if a mirror returns a malformed response (such as corrupted data or encoding issues), the error recovery code does not recognize this as a reason to try alternative URLs. A bad response from one source should not prevent trying another.

## Expected Behavior

1. When `uv self update` runs, it should attempt to fetch the version manifest from the Astral mirror endpoint first. If that fails, it should fall back to the canonical GitHub URL. This mirror-first-then-Github fallback behavior is already implemented for the `ruff` binary and should be replicated for `uv`.

   - The mirror URL is constructed using the `VERSIONS_MANIFEST_MIRROR` constant; the fallback uses `VERSIONS_MANIFEST_URL`.

2. Errors that indicate a malformed manifest response should trigger the fallback mechanism to try alternative URLs. Specifically:
   - When a manifest cannot be parsed (corrupted data), the fallback should be attempted
   - When a manifest has invalid UTF-8 encoding, the fallback should be attempted

   Currently, only network-level errors like download failures, manifest fetch failures, and stream errors trigger the fallback; parse and encoding errors do not.

## Symptoms

- `uv self update` relies solely on GitHub's CDN and does not attempt the Astral mirror first
- When a mirror returns a malformed or corrupted manifest, the update fails immediately instead of trying the next available URL
- The `ruff` binary handles both these cases correctly, but `uv` does not

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `typos (spell-check)`
