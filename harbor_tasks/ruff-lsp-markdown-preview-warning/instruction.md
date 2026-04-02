# Bug: Ruff LSP silently skips markdown files when preview is disabled

## Description

When a user opens a markdown file in their editor and invokes "Format Document" through ruff's LSP server, the file is silently skipped if preview mode is not enabled. There's no warning, no diagnostic, no feedback at all — the user is left wondering why their markdown file isn't being formatted.

The relevant code path is in `crates/ruff_server/src/format.rs`. When the source type is `SourceType::Markdown` and preview mode is off, the format function currently logs a `tracing::warn!` to the server's internal log (which users rarely see) and returns `Ok(None)`, which the caller interprets as "no changes needed" — indistinguishable from a file that is already correctly formatted.

The format request handlers in `crates/ruff_server/src/server/api/requests/format.rs` currently treat `None` from the format function as "nothing to do" with no special handling for the markdown-preview case. The `format_full_document` and `format_document` functions have no way to distinguish between "file unchanged" and "file skipped because it requires preview mode."

## Expected behavior

When a markdown file is formatted without preview mode enabled, the LSP server should display a visible warning to the user (e.g., via `window/showMessage`) explaining that markdown formatting requires preview mode, so they know how to enable it.

## Files of interest

- `crates/ruff_server/src/format.rs` — the `format_internal` function, specifically the `SourceType::Markdown` branch
- `crates/ruff_server/src/server/api/requests/format.rs` — format request handlers that consume the format result
- `crates/ruff_server/src/server/api/requests/execute_command.rs` — command handler that calls `format_full_document`
