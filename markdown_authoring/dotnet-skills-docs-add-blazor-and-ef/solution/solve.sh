#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "<ExcludeByAttribute>Obsolete,GeneratedCodeAttribute,CompilerGeneratedAttribute,E" "skills/crap-analysis/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/crap-analysis/SKILL.md b/skills/crap-analysis/SKILL.md
@@ -66,11 +66,11 @@ Create a `coverage.runsettings` file in your repository root. The **OpenCover fo
           <!-- Exclude test and benchmark assemblies -->
           <Exclude>[*.Tests]*,[*.Benchmark]*,[*.Migrations]*</Exclude>
 
-          <!-- Exclude generated code and obsolete members -->
-          <ExcludeByAttribute>Obsolete,GeneratedCodeAttribute,CompilerGeneratedAttribute</ExcludeByAttribute>
+          <!-- Exclude generated code, obsolete members, and explicit exclusions -->
+          <ExcludeByAttribute>Obsolete,GeneratedCodeAttribute,CompilerGeneratedAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>
 
-          <!-- Exclude source-generated files -->
-          <ExcludeByFile>**/obj/**/*,**/*.g.cs,**/*.designer.cs</ExcludeByFile>
+          <!-- Exclude source-generated files, Blazor generated code, and migrations -->
+          <ExcludeByFile>**/obj/**/*,**/*.g.cs,**/*.designer.cs,**/*.razor.g.cs,**/*.razor.css.g.cs,**/Migrations/**/*</ExcludeByFile>
 
           <!-- Exclude test projects -->
           <IncludeTestAssembly>false</IncludeTestAssembly>
@@ -92,8 +92,8 @@ Create a `coverage.runsettings` file in your repository root. The **OpenCover fo
 |--------|---------|
 | `Format` | Must include `opencover` for complexity metrics |
 | `Exclude` | Exclude test/benchmark assemblies by pattern |
-| `ExcludeByAttribute` | Skip generated and obsolete code |
-| `ExcludeByFile` | Skip source-generated files |
+| `ExcludeByAttribute` | Skip generated, obsolete, and explicitly excluded code (includes `ExcludeFromCodeCoverageAttribute`) |
+| `ExcludeByFile` | Skip source-generated files, Blazor components, and migrations |
 | `SkipAutoProps` | Don't count auto-properties as branches |
 
 ---
@@ -357,7 +357,11 @@ The recommended `coverage.runsettings` excludes:
 | `[*.Migrations]*` | Database migrations (generated) |
 | `GeneratedCodeAttribute` | Source generators |
 | `CompilerGeneratedAttribute` | Compiler-generated code |
+| `ExcludeFromCodeCoverageAttribute` | Explicit developer opt-out |
 | `*.g.cs`, `*.designer.cs` | Generated files |
+| `*.razor.g.cs` | Blazor component generated code |
+| `*.razor.css.g.cs` | Blazor CSS isolation generated code |
+| `**/Migrations/**/*` | EF Core migrations (auto-generated) |
 | `SkipAutoProps` | Auto-properties (trivial branches) |
 
 ---
PATCH

echo "Gold patch applied."
