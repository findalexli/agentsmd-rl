# Fix Exception thrown on .NET 10 Windows when calling Permissions.CheckStatusAsync<Permissions.Microphone>()

## Problem

On .NET 10 Windows, calling `Permissions.CheckStatusAsync<Permissions.Microphone>()` throws an exception when the app is running as an **unpackaged app**.

This is a regression introduced after Windows apps were changed to run as unpackaged by default. In unpackaged apps, `AppxManifest.xml` is not used, so microphone capabilities declared in the manifest are ignored. However, the current implementation always validates microphone capability declarations against `AppxManifest.xml`, which causes an exception for unpackaged apps.

The exception occurs because `EnsureDeclared()` is called unconditionally in both `CheckStatusAsync()` and `RequestAsync()` methods of the `Microphone` permission class on Windows.

## Expected Behavior

1. **Code Fix**: The Windows microphone permission logic should skip manifest capability checks for unpackaged apps. The microphone declaration check should only be required for packaged apps (`AppInfoUtils.IsPackagedApp == true`).

   - In `CheckStatusAsync()`: Only call `EnsureDeclared()` when `AppInfoUtils.IsPackagedApp` is true
   - In `RequestAsync()`: Only call `EnsureDeclared()` when `AppInfoUtils.IsPackagedApp` is true

2. **Config Update**: Remove the stale "Are you waiting for the changes in this PR to be merged?" note from the Copilot instruction files. This note is now redundant because a dogfooding comment bot automatically posts testing instructions under each PR.

## Files to Look At

- `src/Essentials/src/Permissions/Permissions.windows.cs` — Windows-specific microphone permission implementation
- `.github/copilot-instructions.md` — Main Copilot instructions file
- `.github/skills/pr-finalize/SKILL.md` — PR finalization skill documentation
- `.github/skills/pr-finalize/references/complete-example.md` — Example PR description reference

## References

- Issue: #32989
- This is a **Windows-specific** issue affecting unpackaged apps only
