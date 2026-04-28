# Fix Exception thrown on .NET 10 Windows when calling Permissions.CheckStatusAsync<Permissions.Microphone>()

## Problem

On .NET 10 Windows, calling `Permissions.CheckStatusAsync<Permissions.Microphone>()` and `Permissions.RequestAsync<Permissions.Microphone>()` throws an exception when the app is running as an **unpackaged app**.

In unpackaged apps, `AppxManifest.xml` is not used, so capabilities declared in the manifest are not available. The `Microphone` permission class in `src/Essentials/src/Permissions/Permissions.windows.cs` calls `EnsureDeclared()` to validate that microphone capabilities are declared in the app manifest. For unpackaged apps, there is no manifest to validate against, so this validation fails.

The codebase provides several relevant APIs:
- `AppInfoUtils.IsPackagedApp` — indicates whether the app is running as a packaged or unpackaged app
- `EnsureDeclared()` — validates that required capabilities are declared in the app manifest
- `CheckStatus()` — returns the current device access status
- `MediaCaptureInitializationSettings` — configures Windows media capture for permission requests

## Expected Behavior

Calling `Permissions.CheckStatusAsync<Permissions.Microphone>()` on an unpackaged Windows app should return the current permission status (e.g., `Granted`, `Denied`, `Unknown`) without throwing an exception.

Calling `Permissions.RequestAsync<Permissions.Microphone>()` on an unpackaged Windows app should request microphone access and return the resulting permission status without throwing an exception.

The `RequestAsync()` method should check the current status first with `var status = CheckStatus()` before attempting any permission request or manifest validation.

Manifest validation should only occur for packaged apps. The code should use `if (AppInfoUtils.IsPackagedApp)` to guard any `EnsureDeclared()` calls.

The permission-requesting logic in `RequestAsync()` (which uses `MediaCaptureInitializationSettings`) should be extracted into a separate method with the signature `async Task<PermissionStatus> TryRequestPermissionAsync()`.

## Code Style Requirements

The repository enforces C# code formatting via `dotnet format`. Before completing, verify your changes meet the formatting standard:

```
dotnet format src/Essentials/src/Essentials.csproj --no-restore --verify-no-changes --include src/Essentials/src/Permissions/Permissions.windows.cs
```

## Files to Look At

- `src/Essentials/src/Permissions/Permissions.windows.cs` — Windows-specific permission implementations including the `Microphone` class

## References

- Issue: #32989
- This is a **Windows-specific** issue affecting unpackaged apps only
