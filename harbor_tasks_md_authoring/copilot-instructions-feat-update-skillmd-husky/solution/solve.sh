#!/usr/bin/env bash
set -euo pipefail

cd /workspace/copilot-instructions

# Idempotency guard
if grep -qF "- `.NET SDK 10.0+`" "skills/setup-husky-dotnet/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/setup-husky-dotnet/SKILL.md b/skills/setup-husky-dotnet/SKILL.md
@@ -19,7 +19,7 @@ Install and configure Husky Git hooks for .NET projects using **dotnet tool** (n
 ## Critical: .NET Tool Only
 
 **Husky (dotnet tool)** is pure .NET. Your environment needs:
-- `.NET SDK 6.0+`
+- `.NET SDK 10.0+`
 - `dotnet` CLI available in PATH
 - `git` initialized
 
PATCH

echo "Gold patch applied."
