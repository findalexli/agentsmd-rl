# Add configurable vulnerability service backend to `uv audit`

## Problem

The `uv audit` command currently has a hardcoded OSV API endpoint. There's no way for users to:

1. Point `uv audit` at a different vulnerability service URL (e.g., a self-hosted OSV mirror, or a corporate proxy).
2. Select a different vulnerability service format/protocol in the future (the architecture only supports OSV, with no extension point for alternatives).

The relevant code is in `crates/uv/src/commands/project/audit.rs`. The `audit()` function constructs the OSV client with a hardcoded URL parsed from `osv::API_BASE`, and there's no CLI flag or settings path to override it.

## Expected Behavior

- `uv audit` should accept a `--service-format` flag that selects the vulnerability service protocol (currently only `osv`, but the architecture should support future additions).
- `uv audit` should accept a `--service-url` flag that overrides the default API endpoint for the selected service.
- When `--service-url` is not provided, the default URL for the selected format should be used (e.g., `https://api.osv.dev/` for OSV).
- The `VulnerabilityServiceFormat` enum should live in `crates/uv-audit/src/service/mod.rs` and be usable as a clap `ValueEnum`.

## Files of Interest

- `crates/uv-audit/src/service/mod.rs` — service module, currently only re-exports `osv`
- `crates/uv-audit/Cargo.toml` — dependencies for the audit crate
- `crates/uv-cli/src/lib.rs` — CLI argument definitions (`AuditArgs` struct)
- `crates/uv-cli/Cargo.toml` — CLI crate dependencies
- `crates/uv/src/commands/project/audit.rs` — the `audit()` function implementation
- `crates/uv/src/settings.rs` — `AuditSettings` struct and construction
- `crates/uv/src/lib.rs` — wiring of settings to the audit command
