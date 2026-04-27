#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/openai-agents-js
cd "$REPO"

# Idempotency: if the patch has already been applied, skip.
if grep -q "RunReasoningItem" packages/agents-core/src/extensions/handoffFilters.ts; then
  echo "Gold patch already applied; nothing to do."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/agents-core/src/extensions/handoffFilters.ts b/packages/agents-core/src/extensions/handoffFilters.ts
index b88aa74d6..aae5fc69e 100644
--- a/packages/agents-core/src/extensions/handoffFilters.ts
+++ b/packages/agents-core/src/extensions/handoffFilters.ts
@@ -3,6 +3,8 @@ import {
   RunHandoffCallItem,
   RunHandoffOutputItem,
   RunItem,
+  RunReasoningItem,
+  RunToolApprovalItem,
   RunToolCallItem,
   RunToolCallOutputItem,
   RunToolSearchCallItem,
@@ -22,6 +24,7 @@ const TOOL_TYPES = new Set([
   'apply_patch_call',
   'apply_patch_call_output',
   'hosted_tool_call',
+  'reasoning',
 ]);

 /**
@@ -59,7 +62,9 @@ function removeToolsFromItems(items: RunItem[]): RunItem[] {
       !(item instanceof RunToolSearchCallItem) &&
       !(item instanceof RunToolSearchOutputItem) &&
       !(item instanceof RunToolCallItem) &&
-      !(item instanceof RunToolCallOutputItem),
+      !(item instanceof RunToolCallOutputItem) &&
+      !(item instanceof RunReasoningItem) &&
+      !(item instanceof RunToolApprovalItem),
   );
 }

PATCH

echo "Gold patch applied."
