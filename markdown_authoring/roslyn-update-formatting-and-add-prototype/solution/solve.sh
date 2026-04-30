#!/usr/bin/env bash
set -euo pipefail

cd /workspace/roslyn

# Idempotency guard
if grep -qF "- **Namespace Strategy**: `Microsoft.CodeAnalysis.[Language].[Area]` (e.g., `Mic" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -57,18 +57,19 @@ var symbolInfo = semanticModel.GetSymbolInfo(expression);
 
 ## Critical Integration Points
 
-**Language Server Protocol**: `src/LanguageServer/` contains LSP implementation used by VS Code extension
-**ServiceHub**: Remote services (`src/Workspaces/Remote/`) run out-of-process for performance
-**Analyzers**: `src/Analyzers/` for static analysis, separate from `src/RoslynAnalyzers/` (internal tooling)
-**VSIX Packaging**: Multiple deployment targets - `src/VisualStudio/Setup/` for main VS integration
+- **Language Server Protocol**: `src/LanguageServer/` contains LSP implementation used by VS Code extension
+- **ServiceHub**: Remote services (`src/Workspaces/Remote/`) run out-of-process for performance
+- **Analyzers**: `src/Analyzers/` for static analysis, separate from `src/RoslynAnalyzers/` (internal tooling)
+- **VSIX Packaging**: Multiple deployment targets - `src/VisualStudio/Setup/` for main VS integration
 
 ## Key Conventions
 
-**Namespace Strategy**: `Microsoft.CodeAnalysis.[Language].[Area]` (e.g., `Microsoft.CodeAnalysis.CSharp.Formatting`)
-**File Organization**: Group by feature area, separate language-specific implementations
-**Immutability**: All syntax trees, documents, and solutions are immutable - create new instances for changes
-**Cancellation**: Always thread `CancellationToken` through async operations
-**MEF Lifecycle**: Use `[ImportingConstructor]` with obsolete attribute for MEF v2 compatibility
+- **Namespace Strategy**: `Microsoft.CodeAnalysis.[Language].[Area]` (e.g., `Microsoft.CodeAnalysis.CSharp.Formatting`)
+- **File Organization**: Group by feature area, separate language-specific implementations
+- **Immutability**: All syntax trees, documents, and solutions are immutable - create new instances for changes
+- **Cancellation**: Always thread `CancellationToken` through async operations
+- **MEF Lifecycle**: Use `[ImportingConstructor]` with obsolete attribute for MEF v2 compatibility
+- **PROTOTYPE Comments**: Only used to track follow-up work in feature branches and are disallowed in main branch
 
 ## Common Gotchas
 
@@ -84,4 +85,4 @@ var symbolInfo = semanticModel.GetSymbolInfo(expression);
 - `docs/contributing/Building, Debugging, and Testing on Unix.md` - Development setup
 - `src/Compilers/Core/Portable/` - Core compiler APIs
 - `src/Workspaces/Core/Portable/` - Workspace object model
-- Solution filters: `Roslyn.sln`, `Compilers.slnf`, `Ide.slnf` for focused builds
\ No newline at end of file
+- Solution filters: `Roslyn.sln`, `Compilers.slnf`, `Ide.slnf` for focused builds
PATCH

echo "Gold patch applied."
