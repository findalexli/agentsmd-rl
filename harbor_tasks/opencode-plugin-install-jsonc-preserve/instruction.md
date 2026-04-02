# Plugin install strips JSONC comments from config files

When using the plugin installation system in `packages/opencode/src/plugin/install.ts`, any JSONC comments in the user's configuration files (`.opencode/opencode.jsonc`, `.opencode/tui.jsonc`) are silently removed.

## Steps to reproduce

1. Create a `.opencode/opencode.jsonc` file with comments:
   ```jsonc
   {
     // Server configuration
     "plugin": [
       // Analytics plugin, required by ops team
       "analytics@1.0.0"
     ],
     // Keep this trailing note
     "model": "default"
   }
   ```
2. Install a new plugin (e.g., via `patchPluginConfig` or the plug CLI command)
3. Observe that all JSONC comments have been removed from the config file

## Expected behavior

Comments in `.jsonc` config files should be preserved when plugin entries are added or replaced.

## Relevant code

The plugin config patching logic lives in `packages/opencode/src/plugin/install.ts`, specifically the `patchPluginList` and `patchOne` functions. The module already imports from `jsonc-parser` (`applyEdits`, `modify`, `parse`).

The same comment-stripping occurs for both "add" (new plugin) and "replace" (force-updating existing plugin version) operations, across both server and TUI config files.
