#!/usr/bin/env bash
set -euo pipefail

cd /workspace/android-libraries

# Idempotency guard
if grep -qF "Creates .NET for Android bindings for Google's Java/Kotlin libraries (AndroidX, " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,253 +1,103 @@
 # Copilot Instructions for .NET Android Libraries Repository
 
-**Note**: Always update `copilot-instructions.md` with new/relevant information to keep GitHub Copilot suggestions current and accurate.
+**Note**: Update this file with new learnings to keep suggestions accurate.
 
 ## Repository Overview
 
-This repository creates and maintains .NET for Android bindings for Google's Java/Kotlin Android libraries, including:
-- AndroidX libraries (600+ packages)
-- Google Play Services 
-- Firebase
-- ML Kit
-- Various third-party dependencies
+Creates .NET for Android bindings for Google's Java/Kotlin libraries (AndroidX, Play Services, Firebase, ML Kit, etc.) using a **config-driven approach** with `config.json` and the "binderator" tool.
 
-The repository uses a **config-driven approach** where all bindings are defined in `config.json` and automatically generated using the "binderator" tool.
+## Key Files & Directories
+- **`config.json`**: Master config for 600+ Maven artifacts → NuGet packages. Update via `dotnet cake --target=update-config` or `bump-config`, not manually.
+- **`build.cake`**: Main Cake build script
+- **`source/{groupId}/{artifactId}/`**: Binding customizations (Additions/, Transforms/, Metadata.xml)
+- **`generated/`**: Auto-generated projects (not in source control)
+- **`source/AssemblyInfo.cs`**: **DO NOT EDIT** - contains placeholder tokens
 
-## Key Architecture Components
-
-### Core Files
-- **`config.json`**: Master configuration containing all 600+ Maven artifacts to bind, their versions, and NuGet package information
-- **`build.cake`**: Main Cake build script orchestrating the entire build process
-- **`BUILDING.md`**: Comprehensive build instructions and prerequisites
-- **`source/AssemblyInfo.cs`**: Contains build metadata placeholders that are replaced during the build process. **DO NOT EDIT** this file or modify the placeholder tokens - always revert any changes to maintain the original placeholder format.
-
-
-### Directory Structure
-- **`source/`**: Contains binding customizations organized by Maven groupId (e.g., `androidx.core`, `com.google.android.gms`) and Razor templates (`.cshtml` files)
-- **`util/Xamarin.AndroidBinderator/`**: The "binderator" tool that generates binding projects from config
-- **`generated/`**: Auto-generated binding projects (created during build, not in source control)
-- **`docs/`**: Additional documentation including artifact lists and development tips
-
-## Build System
-
-### Prerequisites
-- a recent .NET SDK
-- Cake .NET Tool: `dotnet tool install -g cake.tool`
-- Microsoft OpenJDK 21
-- Android SDK and `$ANDROID_SDK_ROOT` environment variable
-- Optional: `api-tools` for API diffs: `dotnet tool install -g api-tools`
+## Target Frameworks
+- `net9.0-android` (API 35) and `net10.0-android` (API 36)
+- Legacy Xamarin.Android support ended May 1, 2024
 
-### Common Build Commands
+## Common Build Commands
 ```bash
-# Full build of all packages
-dotnet cake
-
-# Clean build for CI
-dotnet cake -t=ci
-
-# Build specific target
-dotnet cake --target=libs
-dotnet cake --target=nuget
-dotnet cake --target=packages
-
-# Update config to latest Maven versions
-dotnet cake --target=update-config
-
-# Bump NuGet package versions (4th component)
-dotnet cake --target=bump-config
-
-# Generate API differences
-dotnet cake nuget-diff.cake
-
-# Run utilities (governance, mappings, etc.)
-dotnet cake utilities.cake
+dotnet cake                        # Full build
+dotnet cake -t=ci                  # CI build
+dotnet cake --target=libs          # Build libraries only
+dotnet cake --target=binderate     # Regenerate projects from config
+dotnet cake --target=update-config # Update to latest Maven versions
+dotnet cake --target=bump-config   # Increment NuGet revision (4th component)
 ```
 
-## Configuration System
-
-### config.json Structure
-**Note**: This file is normally updated using Cake build targets (`update-config`, `bump-config`) rather than manual editing.
-
-Each artifact entry contains:
+## config.json Entry Structure
 ```json
 {
   "groupId": "androidx.activity",
   "artifactId": "activity", 
-  "version": "1.10.1",
-  "nugetVersion": "1.10.1.2",
+  "version": "1.10.1",           // Maven version
+  "nugetVersion": "1.10.1.2",    // 4th component for NuGet-only changes
   "nugetId": "Xamarin.AndroidX.Activity",
-  "dependencyOnly": false  // true for transitive deps only
+  "dependencyOnly": false        // true = transitive dep, no standalone package
 }
 ```
 
-### Version Conventions
-- **Major.Minor.Patch**: Mirrors the Maven artifact version
-- **Revision (4th component)**: Used for NuGet-only updates without Maven changes
-- **Pre-release suffixes**: Supported (e.g., "1.0.0.1-alpha05")
-
-## Development Workflow
-
-### Adding New Bindings
-1. Add artifact entry to `config.json`
-2. Run `dotnet cake --target=binderate` to generate projects
-3. Add any necessary customizations in `source/{groupId}/{artifactId}/`
-4. Build and test: `dotnet cake --target=libs`
-
-### Updating Existing Bindings
-1. Use `dotnet cake --target=update-config` for automatic updates
-2. Or manually edit versions in `config.json`
-3. Run `dotnet cake --target=binderate-diff` to see changes
-4. Build and validate
-
-### Version Bumping
-- Use `dotnet cake --target=bump-config` to increment revision numbers
-- This updates only non-dependency packages (where `dependencyOnly != true`)
-
-### Release Process
-1. Tag commit: `git tag YYYYMMDD-weekly-stable-updates-YYYYMMDD`
-2. Push tag: `git push upstream <tag>`
-3. Use AndroidX Push NuGet.org pipeline in Azure DevOps
-
-## Binding Customizations
-
-### Per-Artifact Customizations
-Located in `source/{groupId}/{artifactId}/`:
-- **`Additions/`**: Additional C# code to add to generated bindings
-- **`Transforms/`**: XML transforms to modify generated API
-- **`Metadata.xml`**: Binding metadata and parameter names
-- **`merge.targets`**: Custom MSBuild targets to include
+## Binding Customizations (in `source/{groupId}/{artifactId}/`)
+- **`Additions/*.cs`**: Extra C# code added to bindings
+- **`Metadata.xml`**: Fix parameter names, remove problematic APIs
+- **`Transforms/`**: XML transforms for generated API
+- **`merge.targets`**: Custom MSBuild targets
 
 ### Common Metadata Patterns
-For comprehensive guidance on troubleshooting binding issues, see: https://github.com/dotnet/java-interop/wiki/Troubleshooting-Android-Bindings-Issues
-
-```xml
-<!-- Remove problematic APIs -->
-<remove-node path="/api/package[@name='com.example']/class[@name='ProblematicClass']" />
-
-<!-- Fix parameter names -->
-<attr path="/api/package[@name='com.example']/class[@name='Example']/method[@name='example']/parameter[@name='p0']" name="name">properName</attr>
-
-<!-- Add managed wrapper -->
-<add-node path="/api/package[@name='com.example']">
-  <class abstract="false" deprecated="not deprecated" final="false" name="ManagedWrapper" static="false" visibility="public">
-  </class>
-</add-node>
-```
-
-### Changing Package/Namespace Names
-
-To change the C# namespace for a Java package (e.g., fixing casing issues), use `Metadata.xml` with the `managedName` attribute. **Do NOT use `rootNamespace` metadata in config.json** - it does not work for namespace changes.
-
-Create `source/{groupId}/{artifactId}/Transforms/Metadata.xml`:
-
 ```xml
-<metadata>
-    <!-- Fix namespace casing: androidx.navigationevent -> AndroidX.NavigationEvent -->
-    <attr 
-        path="/api/package[@name='androidx.navigationevent']" 
-        name="managedName"
-        >
-        AndroidX.NavigationEvent
-    </attr>
-</metadata>
-```
-
-This approach:
-1. Uses the binding generator's transform system
-2. Properly renames the managed namespace during code generation
-3. Is applied at build time when the bindings are generated
-
-## Target Frameworks
-
-### Current Support
-- **Primary**: `net9.0-android` (API 21+)
-- **Migration**: `net10.0-android` (API 35+) - migration capability exists but not currently enabled
-- **Legacy**: Xamarin.Android support ended May 1, 2024
-
-## Code Organization Patterns
-
-### Generated Projects
-- Follow pattern: `{groupId}.{artifactId}.csproj`
-- Located in `generated/` directory
-- Include auto-generated targets files: `{nugetId}.targets`
-
-### NuGet Package Structure
-```
-lib/
-  net9.0-android35.0/
-    {assembly}.dll
-  net10.0-android36.0/
-    {assembly}.dll
-build/
-  net9.0-android35.0/
-    {package}.targets
-  net10.0-android36.0/
-    {package}.targets
-```
-
-## Testing and Validation
-
-### Available Test Targets
-- **`all-packages-tests`**: Run test suite on built packages
-- **`build-run-all-packages-tests`**: Build then test all packages
-- **`api-diff`**: Generate API difference reports
-- **`binderate-config-verify`**: Validate config.json format
-- **`metadata-verify`**: Check binding metadata
+<!-- Remove problematic API -->
+<remove-node path="/api/package[@name='com.example']/class[@name='Problematic']" />
 
-### Quality Checks
-- **Namespace verification**: `dotnet cake utilities.cake -t=namespace-check`
-- **Spell checking**: `dotnet cake utilities.cake -t=spell-check`
-- **Target SDK verification**: `dotnet cake utilities.cake -t=target-sdk-version-check`
+<!-- Fix parameter name -->
+<attr path="//method[@name='example']/parameter[@name='p0']" name="name">properName</attr>
 
-## Documentation Resources
-
-### Internal Documentation
-- **`BUILDING.md`**: Comprehensive build instructions
-- **`docs/development-tips.md`**: Workflow tips and release procedures
-- **`docs/artifact-list.md`**: Complete Maven-to-NuGet mappings
-- **`.github/CONTRIBUTING.md`**: Contribution guidelines
-
-### External Resources
-- [.NET for Android Documentation](https://learn.microsoft.com/en-us/dotnet/android/)
-- [AndroidX Release Notes](https://developer.android.com/jetpack/androidx/versions/stable-channel)
-- [Google Play Services Release Notes](https://developers.google.com/android/guides/releases)
-
-## Common Binding Issues and Solutions
-
-### Interface Implementation Issues
-When a generated class doesn't implement interface methods with the correct signature, typically showing errors like:
-```
-error CS0535: 'ClassName' does not implement interface member 'IInterface.Method(IEncoder, Object?)'
+<!-- Change managed namespace -->
+<attr path="/api/package[@name='androidx.example']" name="managedName">AndroidX.Example</attr>
 ```
 
-This occurs when Java allows method overloading with different parameter types, but C# requires exact interface implementation. 
+Reference: https://github.com/dotnet/java-interop/wiki/Troubleshooting-Android-Bindings-Issues
 
-**Solution**: Create an Additions file with a method that matches the interface signature and calls the strongly-typed method:
+## Common Issues and Fixes
 
+### CS0535: Interface Implementation Mismatch
+When Java method overloading doesn't map to C# interface requirements:
 ```csharp
+// Add in source/{groupId}/{artifactId}/Additions/ClassName.cs
 namespace PackageName;
-
 public partial class ClassName
 {
     public unsafe void Method(IEncoder encoder, Java.Lang.Object? value)
-    {
-        this.Method(encoder, (SpecificType?) value);
-    }
+        => this.Method(encoder, (SpecificType?) value);
 }
 ```
 
-Place this in `source/{groupId}/{artifactId}/Additions/ClassName.cs`.
+### Build File Locking Errors (XARLP7024)
+Transient parallel build issue. Usually resolves on retry. If persistent, may need to reduce build parallelism in `build/cake/build-and-package.cake`.
 
-### Reference Documentation
-- **`docs/development-tips.md`**: Contains detailed examples of common binding fixes
-- [Java Interop Troubleshooting Guide](https://github.com/dotnet/java-interop/wiki/Troubleshooting-Android-Bindings-Issues): Comprehensive binding issue resolution
+### Identifying Failing Package from Build Logs
+Look for the `.csproj` path in error messages:
+```
+[C:\...\generated\{groupId}.{artifactId}\{groupId}.{artifactId}.csproj::TargetFramework=net10.0-android36.0]
+```
+The `{groupId}.{artifactId}` maps to the Maven coordinates and customization folder.
 
-## Best Practices for Contributors
+## Validation Commands
+```bash
+dotnet cake utilities.cake -t=namespace-check
+dotnet cake utilities.cake -t=spell-check  
+dotnet cake --target=metadata-verify
+dotnet cake --target=binderate-config-verify
+```
 
-### Before Making Changes
-1. Read `BUILDING.md` for full setup instructions
-2. Ensure all prerequisites are installed
-3. Run `dotnet cake -t=ci` to verify clean build
-4. Check existing issues and PRs for related work
+## Internal Documentation
+- **`BUILDING.md`**: Full build prerequisites and setup
+- **`docs/development-tips.md`**: Workflow tips, release procedures
+- **`docs/artifact-list.md`**: Complete Maven → NuGet mappings
 
-This repository represents a critical piece of the .NET ecosystem for Android development, enabling C# developers to use the full range of modern Android libraries through automatically maintained bindings.
\ No newline at end of file
+## External Resources
+- [.NET for Android Docs](https://learn.microsoft.com/en-us/dotnet/android/)
+- [AndroidX Release Notes](https://developer.android.com/jetpack/androidx/versions/stable-channel)
+- [Google Play Services Release Notes](https://developers.google.com/android/guides/releases)
+- [Java Interop Troubleshooting](https://github.com/dotnet/java-interop/wiki/Troubleshooting-Android-Bindings-Issues)
PATCH

echo "Gold patch applied."
