# Fix Exception thrown on .NET 10 Windows when calling Permissions.CheckStatusAsync<Permissions.Microphone>()

## Problem

On .NET 10 Windows, calling `Permissions.CheckStatusAsync<Permissions.Microphone>()` throws an exception when the app is running as an **unpackaged app**.

This is a regression introduced after Windows apps were changed to run as unpackaged by default. In unpackaged apps, `AppxManifest.xml` is not used, so microphone capabilities declared in the manifest are not available. However, the current implementation always validates microphone capability declarations against `AppxManifest.xml`, which causes an exception for unpackaged apps.

The exception occurs because the manifest capability check (`EnsureDeclared()`) is called unconditionally in both `CheckStatusAsync()` and `RequestAsync()` methods of the `Microphone` permission class on Windows. The fix should only perform this check when the app is packaged (i.e., has a manifest).

## Expected Behavior

1. **Code Fix**: For unpackaged Windows apps, the microphone permission methods must not attempt to validate manifest declarations. The codebase provides `AppInfoUtils.IsPackagedApp` to distinguish between packaged and unpackaged apps.

   The `CheckStatusAsync()` method should check permission status first, then only validate manifest declarations for packaged apps.

   The `RequestAsync()` method should also check current status first and extract the permission-requesting logic into a separate helper method (`TryRequestPermissionAsync`). Manifest validation should only occur for packaged apps.

2. **Config Update**: Remove stale PR-testing notes from the Copilot instruction files. The old note asking "Are you waiting for the changes in this PR to be merged?" is now redundant. References to "Testing-PR-Builds" and the "Opening PRs" section should also be removed. The `complete-example.md` should retain its "Root Cause" section.

## Files to Look At

- `src/Essentials/src/Permissions/Permissions.windows.cs` — Windows-specific microphone permission implementation
- `.github/copilot-instructions.md` — Main Copilot instructions file
- `.github/skills/pr-finalize/SKILL.md` — PR finalization skill documentation
- `.github/skills/pr-finalize/references/complete-example.md` — Example PR description reference

## References

- Issue: #32989
- This is a **Windows-specific** issue affecting unpackaged apps only
