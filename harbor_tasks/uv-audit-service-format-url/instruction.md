# Add configurable vulnerability service backend to `uv audit`

## Problem

The `uv audit` command currently has a hardcoded OSV API endpoint. There's no way for users to:

1. Point `uv audit` at a different vulnerability service URL (e.g., a self-hosted OSV mirror, or a corporate proxy).
2. Select a different vulnerability service format/protocol in the future (the architecture only supports OSV, with no extension point for alternatives).

The relevant code is in `crates/uv/src/commands/project/audit.rs`. The `audit()` function constructs the OSV client with a hardcoded URL parsed from `osv::API_BASE`, and there's no CLI flag or settings path to override it.

## Expected Behavior

- `uv audit` should accept a `--service-format` flag that selects the vulnerability service protocol (currently only `osv`, but the architecture should support future additions).
- `uv audit` should accept a `--service-url` flag that overrides the default API endpoint for the selected service.
- When `--service-url` is not provided, the default URL for the selected format should be used.
- The format selection enum should be usable as a clap `ValueEnum` so it automatically works with clap's argument parsing.

## Requirements Summary

The implementation must satisfy all of the following:

1. A public enum representing vulnerability service formats must exist in the `uv-audit` crate's service module. It must have an `Osv` variant and derive `Copy`, `Clone`, and `Debug`.

2. The CLI must accept `--service-format` with value enum semantics, defaulting to the OSV format.

3. The CLI must accept `--service-url` with URL hinting for shell completion.

4. The audit command function must accept both the format and URL parameters, using a constant from the OSV module as the fallback URL when no override is provided.

5. The settings structure for audit must include fields for both the format and URL.

6. The uv-cli crate must depend on uv-audit with clap support enabled.

7. No bare `.unwrap()` calls may be introduced in the new service-handling code.

8. The format enum must be imported at the top of files that use it.