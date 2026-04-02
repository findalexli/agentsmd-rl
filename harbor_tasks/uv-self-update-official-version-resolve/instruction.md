# uv self-update should resolve versions via the official ndjson manifest

## Problem

Currently, `uv self update` relies entirely on axoupdater (the third-party cargo-dist updater) for version resolution and download. This works, but it doesn't take advantage of uv's own version manifest infrastructure — the same `ndjson` manifests already used for `ruff self update` via the `Binary` enum and `find_matching_version` in `crates/uv-bin-install/src/lib.rs`.

When uv was installed from the official GitHub releases, the self-update command should first try to resolve the target version using the public ndjson version manifest, then hand the resolved version to axoupdater. This gives uv control over version resolution (including pep440 version specifier support) while still delegating the actual binary download/install to axoupdater.

## Desired behavior

1. **Official installs use the manifest path**: When the install receipt indicates the binary came from the official astral-sh/uv GitHub releases (and no installer base URL overrides are in effect), resolve the version via the ndjson manifest before invoking axoupdater.

2. **Non-official installs use the legacy path**: Enterprise/GHE installs or installs with custom base URL overrides should continue using the existing axoupdater-only code path.

3. **Strict version parsing**: If the user specifies an explicit version (e.g., `uv self update 0.10.0`), only accept exact three-part release versions. Inputs like `0.10` or `v1.2.3` that normalize to a different string under pep440 should be rejected with a clear error.

4. **Smart update check**: When requesting a specific version, allow both upgrades and downgrades. When requesting "latest", only update if the resolved version is actually newer than the current one.

5. **Reuse the existing binary infrastructure**: The `Binary` enum in `crates/uv-bin-install/src/lib.rs` already handles manifest resolution and download URL construction for Ruff. Extend it to support uv, following the same pattern but noting that uv doesn't use the Astral CDN mirror (only the canonical source).

## Key files

- `crates/uv-bin-install/src/lib.rs` — the `Binary` enum and related download/manifest infrastructure
- `crates/uv/src/commands/self_update.rs` — the `self_update` command implementation

Look at how `Binary::Ruff` is implemented for the manifest/download pattern to follow. Look at the axoupdater `ReleaseSource` type to understand how to detect the install origin.

## Notes

- The `updater.run()` call and result handling code is used from two code paths now, so it should be extracted to avoid duplication.
- The `EnvVars` module in `uv_static` has the relevant installer override environment variable names.
- Make sure the existing self-update error handling (e.g., rate-limit 403 errors suggesting `--token`) is preserved in both paths.
