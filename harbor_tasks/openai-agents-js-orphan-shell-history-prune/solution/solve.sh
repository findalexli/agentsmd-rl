#!/usr/bin/env bash
# Gold patch: prune orphan hosted shell calls from public history.
# Sourced from openai/openai-agents-js#1102, applied in-tree.
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotency guard: if the helper already exists, the fix is in.
if grep -q "function getContinuationOutputItems" packages/agents-core/src/runner/items.ts; then
  echo "Patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fair-clouds-flow.md b/.changeset/fair-clouds-flow.md
new file mode 100644
index 000000000..3c9cc45aa
--- /dev/null
+++ b/.changeset/fair-clouds-flow.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': patch
+---
+
+fix: prune orphan hosted shell calls from public history
diff --git a/packages/agents-core/src/runner/items.ts b/packages/agents-core/src/runner/items.ts
index 72b82b666..96144f1ac 100644
--- a/packages/agents-core/src/runner/items.ts
+++ b/packages/agents-core/src/runner/items.ts
@@ -200,14 +200,24 @@ export function prepareModelInputItems(
   reasoningItemIdPolicy?: ReasoningItemIdPolicy,
 ): AgentInputItem[] {
   const callerItems = toAgentInputList(originalInput);
-  const generatedOutputItems = extractOutputItemsFromRunItems(
+  const preparedGeneratedItems = getContinuationOutputItems(
     generatedItems,
     reasoningItemIdPolicy,
   );
-  const preparedGeneratedItems = dropOrphanToolCalls(generatedOutputItems);
   return [...callerItems, ...preparedGeneratedItems];
 }

+function getContinuationOutputItems(
+  generatedItems: RunItem[],
+  reasoningItemIdPolicy?: ReasoningItemIdPolicy,
+): AgentInputItem[] {
+  const generatedOutputItems = extractOutputItemsFromRunItems(
+    generatedItems,
+    reasoningItemIdPolicy,
+  );
+  return dropOrphanToolCalls(generatedOutputItems);
+}
+
 /**
  * Constructs the model input array for the current turn by combining the original turn input with
  * any new run items (excluding tool approval placeholders). This helps ensure that repeated calls
@@ -220,7 +230,7 @@ export function getTurnInput(
   generatedItems: RunItem[],
   reasoningItemIdPolicy?: ReasoningItemIdPolicy,
 ): AgentInputItem[] {
-  const outputItems = extractOutputItemsFromRunItems(
+  const outputItems = getContinuationOutputItems(
     generatedItems,
     reasoningItemIdPolicy,
   );
PATCH

echo "Patch applied successfully."
