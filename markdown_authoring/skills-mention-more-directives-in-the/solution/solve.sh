#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: Run single-file C# programs as scripts (file-based apps) for quick " "plugins/dotnet/skills/csharp-scripts/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/dotnet/skills/csharp-scripts/SKILL.md b/plugins/dotnet/skills/csharp-scripts/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: csharp-scripts
-description: Run single-file C# programs as scripts for quick experimentation, prototyping, and concept testing. Use when the user wants to write and execute a small C# program without creating a full project.
+description: Run single-file C# programs as scripts (file-based apps) for quick experimentation, prototyping, and concept testing. Use when the user wants to write and execute a small C# program without creating a full project.
 ---
 
 # C# Scripts
@@ -43,7 +43,7 @@ Console.WriteLine($"Sum: {numbers.Sum()}");
 Guidelines:
 
 - Use top-level statements (no `Main` method, class, or namespace boilerplate)
-- Place `using` directives at the top of the file
+- Place `using` directives at the top of the file (after the `#!` line and any `#:` directives if present)
 - Place type declarations (classes, records, enums) after all top-level statements
 
 ### Step 3: Run the script
@@ -58,9 +58,13 @@ Builds and runs the file automatically. Cached so subsequent runs are fast. Pass
 dotnet hello.cs -- arg1 arg2 "multi word arg"
 ```
 
-### Step 4: Add NuGet packages (if needed)
+### Step 4: Add directives (if needed)
 
-Use the `#:package` directive at the top of the file to reference NuGet packages. Always specify a version:
+Place directives at the top of the file (immediately after an optional shebang line), before any `using` directives or other C# code. All directives start with `#:`.
+
+#### `#:package` — NuGet package references
+
+Always specify a version:
 
 ```csharp
 #:package Humanizer@2.14.1
@@ -70,6 +74,48 @@ using Humanizer;
 Console.WriteLine("hello world".Titleize());
 ```
 
+#### `#:property` — MSBuild properties
+
+Set any MSBuild property inline. Syntax: `#:property PropertyName=Value`
+
+```csharp
+#:property AllowUnsafeBlocks=true
+#:property PublishAot=false
+#:property NoWarn=CS0162
+```
+
+MSBuild expressions and property functions are supported:
+
+```csharp
+#:property LogLevel=$([MSBuild]::ValueOrDefault('$(LOG_LEVEL)', 'Information'))
+```
+
+Common properties:
+
+| Property | Purpose |
+|----------|---------|
+| `AllowUnsafeBlocks=true` | Enable `unsafe` code |
+| `PublishAot=false` | Disable native AOT (enabled by default) |
+| `NoWarn=CS0162;CS0219` | Suppress specific warnings |
+| `LangVersion=preview` | Enable preview language features |
+| `InvariantGlobalization=false` | Enable culture-specific globalization |
+
+#### `#:project` — Project references
+
+Reference another project by relative path:
+
+```csharp
+#:project ../MyLibrary/MyLibrary.csproj
+```
+
+#### `#:sdk` — SDK selection
+
+Override the default SDK (`Microsoft.NET.Sdk`):
+
+```csharp
+#:sdk Microsoft.NET.Sdk.Web
+```
+
 ### Step 5: Clean up
 
 Remove the script file when the user is done. To clear cached build artifacts:
@@ -156,6 +202,8 @@ Replace the generated `Program.cs` with the script content and run with `dotnet
 |---------|----------|
 | `.cs` file is inside a directory with a `.csproj` | Move the script outside the project directory, or use `dotnet run --file file.cs` |
 | `#:package` without a version | Specify a version: `#:package PackageName@1.2.3` or `@*` for latest |
+| `#:property` with wrong syntax | Use `PropertyName=Value` with no spaces around `=` and no quotes: `#:property AllowUnsafeBlocks=true` |
+| Directives placed after C# code | All `#:` directives must appear immediately after an optional shebang line (if present) and before any `using` directives or other C# statements |
 | Reflection-based JSON serialization fails | Use source-generated JSON with `JsonSerializerContext` (see [Source-generated JSON](#source-generated-json)) |
 | Unexpected build behavior or version errors | File-based apps inherit `global.json`, `Directory.Build.props`, `Directory.Build.targets`, and `nuget.config` from parent directories. Move the script to an isolated directory if the inherited settings conflict |
 
PATCH

echo "Gold patch applied."
