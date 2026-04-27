#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotency guard
if grep -qF "- The highest `netN.0` branch (by convention) - For new features and API changes" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -18,8 +18,7 @@ When performing a code review on PRs that change functional code, run the pr-fin
 
 - **.NET SDK** - Version is **ALWAYS** defined in `global.json` at repository root
   - **main branch**: Latest stable .NET version
-  - **net10.0 branch**: .NET 10 SDK
-  - **Feature branches**: Each feature branch (e.g., `net11.0`, `net12.0`) correlates to its respective .NET version
+  - **Feature branches**: Each `netN.0` branch targets the .NET N SDK. By convention, the highest `netN.0` branch is the current development branch for new features and API changes.
 - **Cake build system** for compilation and packaging (`dotnet cake`)
 - **MSBuild** with custom build tasks (must build `Microsoft.Maui.BuildTasks.slnf` first)
 - **Testing frameworks**:
@@ -140,7 +139,7 @@ When working with public API changes:
 
 ### Branching
 - `main` - For bug fixes without API changes
-- `net10.0` - For new features and API changes
+- The highest `netN.0` branch (by convention) - For new features and API changes. To find it, run `git fetch origin` then: `git for-each-ref --sort=-version:refname --count=1 --format='%(refname:lstrip=3)' refs/remotes/origin/net*.0`
 
 ### Git Workflow (Copilot CLI Rules)
 
PATCH

echo "Gold patch applied."
