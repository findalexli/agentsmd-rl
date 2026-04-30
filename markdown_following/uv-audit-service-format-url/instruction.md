# Add configurable vulnerability service backend to `uv audit`

## Problem

The `uv audit` command currently has a hardcoded OSV API endpoint. There's no way for users to:

1. Point `uv audit` at a different vulnerability service URL (e.g., a self-hosted OSV mirror, or a corporate proxy).
2. Select a different vulnerability service format/protocol in the future (the architecture only supports OSV, with no extension point for alternatives).

## Expected Behavior

- `uv audit` should accept a `--service-format` flag that selects the vulnerability service protocol (currently only `osv`, but the architecture should support future additions).
- `uv audit` should accept a `--service-url` flag that overrides the default API endpoint for the selected service.
- When `--service-url` is not provided, the default URL for the selected format should be used. The default URL is the value of the `osv::API_BASE` constant when the OSV format is selected.
- The format selection enum should be usable as a clap `ValueEnum` so it automatically works with clap's argument parsing.

## Requirements Summary

The implementation must satisfy all of the following:

1. A public enum named `VulnerabilityServiceFormat` must exist in the `uv-audit` crate's service module (specifically at `uv_audit::service::VulnerabilityServiceFormat`). It must have an `Osv` variant and derive `Copy`, `Clone`, and `Debug`. When the `clap` feature is enabled, it must also derive `clap::ValueEnum`.

2. The CLI argument struct `AuditArgs` must have a field named `service_format` with type `VulnerabilityServiceFormat`. This field must have clap attributes `value_enum` and `default_value = "osv"`.

3. The CLI argument struct `AuditArgs` must have a field named `service_url` with type `Option<String>`. This field must use `ValueHint::Url` for shell completion.

4. The audit command function must accept both the format and URL parameters, using the constant `osv::API_BASE` as the fallback URL when no override is provided.

5. The settings structure `AuditSettings` must include fields named `service_format` (type `VulnerabilityServiceFormat`) and `service_url` (type `Option<String>`), and must wire these from the CLI arguments.

6. The `uv-cli` crate's `Cargo.toml` must depend on `uv-audit` with the `clap` feature enabled (i.e., `features = ["clap"]`).

7. No bare `.unwrap()` calls may be introduced in the new service-handling code.

8. The `VulnerabilityServiceFormat` enum must be imported at the top of files that use it (not locally imported within functions).

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
