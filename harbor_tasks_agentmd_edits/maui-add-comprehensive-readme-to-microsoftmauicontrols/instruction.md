# Add comprehensive README to Microsoft.Maui.Controls NuGet package

## Problem

The Microsoft.Maui.Controls NuGet package does not include a README.md file, which means users browsing the package on nuget.org see minimal documentation and must navigate elsewhere to understand what the package provides. This reduces package discoverability and creates a poor first impression for new developers.

## Expected Behavior

The NuGet package should include a comprehensive README.md that:
- Appears directly on the NuGet gallery page
- Explains what .NET MAUI is and what the package provides
- Lists supported platforms with minimum versions
- Includes getting started instructions with prerequisites
- Provides code examples for common scenarios
- Links to official documentation and community resources
- Shows NuGet version badge and license information

The csproj must be configured to pack the README into the NuGet package via the `PackageReadmeFile` property.

## Files to Look At

- `src/Controls/src/NuGet/Controls.NuGet.csproj` - The NuGet project file that needs PackageReadmeFile property and None item to pack README.md
- `src/Controls/src/NuGet/README.md` - The new README file that should be created with comprehensive documentation

## Implementation Notes

1. Create a new README.md in the `src/Controls/src/NuGet/` directory with comprehensive package documentation
2. Add `<PackageReadmeFile>README.md</PackageReadmeFile>` to a PropertyGroup in the csproj
3. Add a `<None Include="README.md" Pack="true" PackagePath="\" />` item to include the file in the package
