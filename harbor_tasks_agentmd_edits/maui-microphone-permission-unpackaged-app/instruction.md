# Fix Microphone Permission Exception for Unpackaged Windows Apps

## Problem

On .NET 10 Windows, calling `Permissions.CheckStatusAsync<Permissions.Microphone>()` throws an exception when the app is running as an unpackaged app. This is a regression introduced after Windows apps were changed to run as unpackaged by default.

The root cause is that the `Microphone` permission class always validates microphone capability declarations against `AppxManifest.xml`. In unpackaged apps, `AppxManifest.xml` is not used, so this validation throws an exception.

Both `CheckStatusAsync()` and `RequestAsync()` are affected.

## Expected Behavior

Microphone permission checks should work for both packaged and unpackaged apps. The manifest capability check (`EnsureDeclared`) should only apply to packaged apps, since unpackaged apps don't use `AppxManifest.xml`.

## Files to Look At

- `src/Essentials/src/Permissions/Permissions.windows.cs` -- Contains the `Microphone` permission class with `CheckStatusAsync` and `RequestAsync` methods that unconditionally call `EnsureDeclared()`

## Additional Context

The project's agent instruction files (`.github/copilot-instructions.md` and `.github/skills/pr-finalize/SKILL.md`) currently contain an outdated requirement for PRs to start with a NOTE block asking users to test PR artifacts. This requirement has been retired and should be removed from all agent config files where it appears, including any reference examples. Update the relevant documentation to reflect that PR descriptions no longer need to start with this NOTE block.
