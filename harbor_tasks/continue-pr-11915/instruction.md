# Fix: config.yaml empty file causes missing defaults

## Symptom

When `~/.continue/config.yaml` exists but is **empty**, the Continue core does not populate it with the default configuration. Instead, the file remains empty, which causes downstream errors (e.g., when the gear icon is clicked to open the config profile).

On a clean startup where the file is completely missing, the defaults **are** written correctly. The bug is specifically an **empty-but-present file** case that is not handled.

## Expected Behavior

- If `~/.continue/config.yaml` does not exist → create it with defaults ✓ (already works)
- If `~/.continue/config.yaml` exists but is empty → **populate it with defaults** (currently broken)
- If `~/.continue/config.yaml` exists and has valid content → leave it untouched ✓ (already works)

## What the default config looks like

The default config object written by `getConfigYamlPath()` has these top-level keys:

```yaml
name: "Local Config"
version: "1.0.0"
schema: "v1"
models: []
```

## Where to look

- The file `core/util/paths.ts` contains `getConfigYamlPath()` — this is where the empty-file check is missing.
- The file `core/config/ConfigHandler.ts` calls `getConfigYamlPath()` before opening a local config profile via the gear icon.

## Verification

After fixing, you can verify by:
1. Creating `~/.continue/config.yaml` as an empty file
2. Calling `getConfigYamlPath()` from the TypeScript code
3. Reading the file — it should now contain the default YAML config (name, version, schema, models)

## Notes

- The fix should handle the empty-file case with a simple `trim() === ""` check on the file contents
- A subsequent call to `getConfigYamlPath()` on an already-populated file should not modify it
- The `config.json` file (legacy) should still be checked: if it exists but `config.yaml` does not, `config.yaml` should still be created
