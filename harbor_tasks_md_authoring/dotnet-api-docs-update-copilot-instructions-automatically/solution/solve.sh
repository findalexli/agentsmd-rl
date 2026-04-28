#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-api-docs

# Idempotency guard
if grep -qF "This repo contains the official .NET API reference documentation in ECMAXML form" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,17 +1,120 @@
-Code comments should end with a period.
+# .NET API Reference Docs — Copilot Instructions
 
-When you add a code snippet to the XML remarks of an API, add the code as a separate code file (.cs file) and not as an inline (```) code block. Also add a .csproj file to compile the code if one doesn't already exist in the snippet folder.
+## Repository overview
 
-Don't use the word "may". Use "might" to indicate possibility or "can" to indicate permission.
+This repo contains the official .NET API reference documentation in ECMAXML format. The `xml/` directory holds one XML file per type, organized by namespace (e.g., `xml/System/String.xml`). Documentation is published via DocFX and ECMA2Yaml to [learn.microsoft.com](https://learn.microsoft.com).
 
-There should always be a comma before a clause that begins with "which".
+Some namespaces (notably `Microsoft.Extensions.*`, `System.CommandLine.*`, `System.Formats.*`, `System.Numerics.Tensors.*`) are auto-generated from source code in other repos. Their `open_to_public_contributors` metadata is set to `false` in `docfx.json`. Don't edit those XML files directly.
 
-Use a conversational tone with contractions.
+## Build and validation
 
-Be concise.
+- **Snippet compilation** — The CI workflow "Snippets 5000" compiles all code samples on PRs to `main`. To build a single snippet project locally:
 
-Break up long sentences.
+  ```
+  dotnet build snippets/csharp/System/String/Overview/Project.csproj
+  ```
 
-Use the present tense for instructions and descriptions. For example, "The method returns a value" instead of "The method will return a value."
+- There's no repo-wide `dotnet build` or test command. Validation happens through the OPS (Open Publishing System) build triggered on PRs.
 
-Use the Oxford comma in lists of three or more items.
+## ECMAXML format
+
+Each type file (`xml/<Namespace>/<TypeName>.xml`) follows this structure:
+
+```xml
+<Type Name="TypeName" FullName="Namespace.TypeName">
+  <TypeSignature Language="C#" Value="..." />
+  <AssemblyInfo>...</AssemblyInfo>
+  <Docs>
+    <summary>Brief description.</summary>
+    <remarks>
+      <format type="text/markdown"><![CDATA[
+## Remarks
+Detailed markdown content here.
+      ]]></format>
+    </remarks>
+  </Docs>
+  <Members>
+    <Member MemberName="MethodName">
+      <MemberSignature Language="C#" Value="..." />
+      <MemberType>Method</MemberType>
+      <Docs>
+        <param name="paramName">Description.</param>
+        <summary>Brief description.</summary>
+        <returns>Description.</returns>
+        <remarks>...</remarks>
+        <exception cref="T:System.ArgumentException">Description.</exception>
+      </Docs>
+    </Member>
+  </Members>
+</Type>
+```
+
+Key points:
+
+- Don't edit the `<TypeSignature>`, `<MemberSignature>`, `<AssemblyInfo>`, `<TypeForwardingChain>`, or `<FrameworkAlternate>` elements (or their attributes/values) — they are auto-generated.
+- Editable content lives inside `<Docs>` elements: `<summary>`, `<remarks>`, `<param>`, `<returns>`, `<exception>`, `<example>`, `<seealso>`, and `<altmember>`.
+- Longer content goes inside `<format type="text/markdown"><![CDATA[ ... ]]></format>` blocks, which support full Markdown.
+- Namespace-level docs are in files like `xml/ns-System.xml`.
+
+## Cross-references
+
+Use these patterns to link to other APIs:
+
+- `<see cref="T:System.String" />` — link to a type.
+- `<see cref="M:System.String.Clone" />` — link to a method.
+- `<see cref="P:System.String.Length" />` — link to a property.
+- `<paramref name="value" />` — reference a parameter by name.
+- `<altmember cref="T:System.Text.StringBuilder" />` — "see also" link.
+- Inside markdown (`<format>`) blocks, use `<xref:System.String>` for cross-references.
+
+DocId prefixes: `T:` (type), `M:` (method), `P:` (property), `F:` (field), `E:` (event), `N:` (namespace).
+
+Don't escape backticks or asterisks in xref DocIDs. Use literal `` ` `` and `*` characters, not URL-encoded forms like `%60` or `%2A`. For example, use `` <xref:System.Collections.Generic.List`1> ``, not `<xref:System.Collections.Generic.List%601>`.
+
+## Code snippets
+
+Snippets are standalone compilable projects in `snippets/{language}/{Namespace}/{Type}/`.
+
+### Referencing snippets from XML
+
+Inside a `<format>` CDATA block, reference snippets with:
+
+```markdown
+:::code language="csharp" source="~/snippets/csharp/System/String/Overview/example.cs" id="Snippet1":::
+```
+
+### Snippet file conventions
+
+- Mark regions in source files with `// <Snippet1>` and `// </Snippet1>` comment pairs.
+- Each snippet folder should have a `.csproj` file so the CI can compile it. Use SDK-style projects:
+
+  ```xml
+  <Project Sdk="Microsoft.NET.Sdk">
+    <PropertyGroup>
+      <OutputType>Library</OutputType>
+      <TargetFramework>net10.0</TargetFramework>
+    </PropertyGroup>
+  </Project>
+  ```
+
+- Use `OutputType` of `Exe` if the snippet has a `Main` method or uses top-level statements, or `Library` otherwise.
+- Add NuGet `<PackageReference>` entries if the snippet uses APIs outside the base runtime.
+- Snippet languages: `csharp`, `fsharp`, `visualbasic`. Each goes in its respective `snippets/` subdirectory.
+
+### Reusable includes
+
+Shared markdown fragments live in `includes/` and are referenced from CDATA blocks as:
+
+```markdown
+[!INCLUDE[description](~/includes/filename.md)]
+```
+
+## Writing style
+
+- Code comments should end with a period.
+- Don't use the word "may". Use "might" to indicate possibility or "can" to indicate permission.
+- Always put a comma before a clause that begins with "which".
+- Use a conversational tone with contractions.
+- Be concise. Break up long sentences.
+- Use the present tense. For example, "The method returns a value" instead of "The method will return a value."
+- Use the Oxford comma in lists of three or more items.
PATCH

echo "Gold patch applied."
