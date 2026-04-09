# Respect `--exclude-newer` in `uv tool list --outdated`

## Problem

Running `uv tool list --outdated` shows which installed tools have newer versions available, but there is no way to limit which candidate releases are considered. The `--exclude-newer` flag (which filters packages to those uploaded before a given date) is supported by other resolver-backed subcommands like `uv pip install` and `uv lock`, but `uv tool list` does not accept it.

This means users who pin `exclude-newer` in their `uv.toml` or on the CLI cannot get consistent "outdated" results — `uv tool list --outdated` always checks against the absolute latest release, ignoring the date cutoff.

## Expected Behavior

`uv tool list --outdated` should accept `--exclude-newer` (and respect the `UV_EXCLUDE_NEWER` environment variable and `uv.toml` configuration) to limit which releases count as "newer." When the flag is set, only releases uploaded before the cutoff date should be considered when determining whether a tool is outdated.

The CLI flag should take precedence over filesystem configuration, and both should take precedence over tool-specific stored options — matching the standard option-merging behavior used by other uv subcommands.

## Files to Look At

- `crates/uv-cli/src/lib.rs` — CLI argument definitions, specifically `ToolListArgs`
- `crates/uv/src/settings.rs` — `ToolListSettings` struct and its `resolve()` method
- `crates/uv/src/commands/tool/list.rs` — The `list()` function that checks for outdated tools
- `crates/uv/src/lib.rs` — Top-level command dispatch, wires settings into `list()`
