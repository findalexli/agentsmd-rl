# Bug: `uv tool list --outdated` ignores per-tool resolver settings

## Summary

When a tool is installed with specific resolver settings — such as `--exclude-newer`, custom index locations, `--prerelease`, or keyring configuration — those settings are persisted in the tool's receipt (in `uv-receipt.toml`). The `uv tool upgrade` command correctly reads and respects these per-tool settings when deciding what to upgrade.

However, `uv tool list --outdated` does **not** respect these stored settings. Instead, it constructs a single shared registry client using global defaults (`PrereleaseMode::default()`, `ExcludeNewer::default()`, etc.) for all tools. This means:

1. A tool installed with `--exclude-newer 2024-03-25T00:00:00Z` will still be reported as outdated against the absolute latest version, even though `uv tool upgrade` would correctly skip that upgrade.
2. Tools installed with custom index locations are checked against the default index instead.
3. Prerelease and keyring settings are similarly ignored.

This creates a confusing UX where `uv tool list --outdated` reports upgrades that `uv tool upgrade --all` then says "Nothing to upgrade" for.

## Relevant Code

The issue is in `crates/uv/src/commands/tool/list.rs`, in the `list()` function. Look at how the `LatestClient` is constructed and how the registry client is initialized when `outdated` is true. Compare this with how `uv tool upgrade` handles per-tool settings — each tool's stored options should be used to configure the client for that specific tool's version check.

The iteration over `valid_tools` provides access to each tool's metadata (including `tool.options()`), but the current code doesn't use it.

## Expected Behavior

When checking for outdated tools, each tool should be queried using its own stored resolver/installer settings (prerelease mode, exclude-newer, index locations, keyring provider, etc.), matching the behavior of `uv tool upgrade`.
