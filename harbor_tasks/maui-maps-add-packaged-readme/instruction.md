# Add packaged README for Microsoft.Maui.Controls.Maps

## Problem

The `Microsoft.Maui.Controls.Maps` NuGet package has no README. When developers find the package on NuGet.org, they see no quick-start guide or usage examples. The package project file (`Controls.Maps.csproj`) does not declare a `PackageReadmeFile`, so no documentation is shown to consumers.

## Expected Behavior

A README should be added to the Maps project folder (`src/Controls/Maps/README.md`) that provides quick-start guidance for using the Maps control. This README should cover:

- How to install the NuGet package
- How to enable Maps in `MauiProgram.cs`
- Platform-specific setup (Android API keys, iOS, Windows status)
- Code examples showing how to add a map, place pins, draw shapes, and handle interactions
- Links to the official .NET MAUI Map documentation

The csproj file should be updated to package the README so it appears on NuGet.org.

## Files to Look At

- `src/Controls/Maps/src/Controls.Maps.csproj` — the Maps project file that controls NuGet packaging
- `src/Controls/Maps/` — where the README should be placed

## Notes

The project follows standard .NET MAUI documentation conventions. Reference the existing documentation patterns in the repository when writing the README. The README should be part of the NuGet package so it is visible on NuGet.org.
