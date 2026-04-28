#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bytebase

# Idempotency guard
if grep -qF "When working on React UI, invoke the `shadcn` skill before writing or modifying " "frontend/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/frontend/AGENTS.md b/frontend/AGENTS.md
@@ -15,6 +15,10 @@ This file provides additional guidance to AI coding assistants working under `./
 - All new UI code should be written in React unless an existing Vue surface must be preserved temporarily for compatibility.
 - Do not delete Vue counterparts until you verify they have no remaining live callers.
 
+## shadcn Skill
+
+When working on React UI, invoke the `shadcn` skill before writing or modifying components. The skill provides component selection guidance, critical rules, and best practices. Always check the skill when unsure which component to use.
+
 ## shadcn Component Guidelines
 
 React UI components live in `src/react/components/ui/` and follow shadcn-style patterns: Base UI primitives wrapped with `cva` variants and `cn()` for class merging.
PATCH

echo "Gold patch applied."
