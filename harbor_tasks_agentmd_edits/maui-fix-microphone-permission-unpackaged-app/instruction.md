# Fix Microphone Permission Exception for Unpackaged Windows Apps

## Problem

On .NET 10 Windows, calling `Permissions.CheckStatusAsync<Permissions.Microphone>()` throws an exception when the app is running as an unpackaged app. This is a regression introduced after Windows apps were changed to run as unpackaged by default.

The current implementation unconditionally validates microphone capability declarations against `AppxManifest.xml` via `EnsureDeclared()`. In unpackaged apps, `AppxManifest.xml` is not used, so this validation throws an exception. Both `CheckStatusAsync()` and `RequestAsync()` in the `Microphone` permission class are affected.

## Expected Behavior

Microphone permission checks and requests should work for both packaged and unpackaged apps without throwing. The manifest capability validation should only apply when the app is actually packaged and uses `AppxManifest.xml`.

## Files to Look At

- `src/Essentials/src/Permissions/Permissions.windows.cs` — Contains the `Microphone` permission class with `CheckStatusAsync` and `RequestAsync` methods that unconditionally call `EnsureDeclared()`

## Additional Context

The project's agent instruction files currently contain an outdated requirement for PRs to start with a NOTE block asking users to test PR build artifacts. This requirement has been retired. After making the code fix, update the relevant agent configuration files to remove references to this outdated NOTE block requirement, including any examples that show it.
