# Add packaged README for Microsoft.Maui.Controls.Maps

## Problem

The `Microsoft.Maui.Controls.Maps` NuGet package has no README. When developers find the package on NuGet.org, they see no quick-start guide or usage examples. The package project file (`Controls.Maps.csproj`) does not declare a `PackageReadmeFile`, so no documentation is shown to consumers.

## Expected Behavior

A README should be added to the Maps project folder (`src/Controls/Maps/README.md`) that provides quick-start guidance for using the Maps control. This README should cover:

- How to install the NuGet package
- How to enable Maps in `MauiProgram.cs` using `UseMauiMaps()`
- Platform-specific setup (Android API keys, iOS, Windows status)
- Code examples showing how to add a map, place pins, draw shapes, and handle interactions
- Links to the official .NET MAUI Map documentation at learn.microsoft.com

The csproj file should be updated to package the README so it appears on NuGet.org.

## README Content Requirements

The README at `src/Controls/Maps/README.md` must meet all of the following:

1. **Length**: At least 500 characters of substantial documentation
2. **Installation instructions**: Must include `dotnet add package Microsoft.Maui.Controls.Maps` and mention the full package name
3. **MAUI initialization**: Must show `UseMauiMaps()` for enabling maps in `MauiProgram.cs`
4. **Feature coverage**: Must document at least 3 of: pin, polygon, polyline, circle, MapClicked, MapType, IsShowingUser
5. **Code examples**: Must include XAML with `maps:Map` or C# with `UseMauiMaps`, `MapClickedEventArgs`, `MoveToRegion`, or `MapSpan`
6. **Documentation link**: Must include a link to Microsoft Learn documentation
7. **Structure**: Must start with a markdown heading (`#`) and have subsections (`##`)

## csproj Metadata Requirements

The `src/Controls/Maps/src/Controls.Maps.csproj` file must retain these existing values:
- **Description**: `Maps and mapping support` (do not change)
- **IsPackable**: Must be `true`
- **PackageTags**: Must include the word `maps`
- **PackageId**: Must contain `Microsoft.Maui`

The csproj must also declare a `PackageReadmeFile` property pointing to `README.md` and include `README.md` as a `<None>` item with `Pack="true"` so it is included in the NuGet package.

## Platform Directories

The Maps project has PublicAPI files for the following target frameworks (all must remain intact):
- `net`
- `net-android`
- `net-ios`
- `net-maccatalyst`
- `net-tizen`
- `net-windows`
- `netstandard`

Each platform directory contains `PublicAPI.Shipped.txt` and `PublicAPI.Unshipped.txt` files with `#nullable enable` headers. Do not modify these files.

## Files to Look At

- `src/Controls/Maps/src/Controls.Maps.csproj` — the Maps project file that controls NuGet packaging
- `src/Controls/Maps/` — where the README should be placed

## Notes

The project follows standard .NET MAUI documentation conventions. Reference the existing documentation patterns in the repository when writing the README. The README should be part of the NuGet package so it is visible on NuGet.org.