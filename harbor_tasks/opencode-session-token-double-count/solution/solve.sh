#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

FILE="packages/opencode/src/session/index.ts"

# Idempotency: check if already fixed (the provider-specific check is gone)
if ! grep -q 'excludesCachedTokens' "$FILE" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/session/index.ts b/packages/opencode/src/session/index.ts
index eb01739c156..371091722e3 100644
--- a/packages/opencode/src/session/index.ts
+++ b/packages/opencode/src/session/index.ts
@@ -32,7 +32,6 @@ import { ModelID, ProviderID } from "@/provider/schema"
 import { Permission } from "@/permission"
 import { Global } from "@/global"
 import type { LanguageModelV2Usage } from "@ai-sdk/provider"
-import { iife } from "@/util/iife"
 import { Effect, Layer, Scope, ServiceMap } from "effect"
 import { makeRuntime } from "@/effect/run-service"

@@ -265,27 +264,12 @@ export namespace Session {
         0) as number,
     )

-    // OpenRouter provides inputTokens as the total count of input tokens (including cached).
-    // AFAIK other providers (OpenRouter/OpenAI/Gemini etc.) do it the same way e.g. vercel/ai#8794 (comment)
-    // Anthropic does it differently though - inputTokens doesn't include cached tokens.
-    // It looks like OpenCode's cost calculation assumes all providers return inputTokens the same way Anthropic does (I'm guessing getUsage logic was originally implemented with anthropic), so it's causing incorrect cost calculation for OpenRouter and others.
-    const excludesCachedTokens = !!(input.metadata?.["anthropic"] || input.metadata?.["bedrock"])
-    const adjustedInputTokens = safe(
-      excludesCachedTokens ? inputTokens : inputTokens - cacheReadInputTokens - cacheWriteInputTokens,
-    )
+    // AI SDK v6 normalized inputTokens to include cached tokens across all providers
+    // (including Anthropic/Bedrock which previously excluded them). Always subtract cache
+    // tokens to get the non-cached input count for separate cost calculation.
+    const adjustedInputTokens = safe(inputTokens - cacheReadInputTokens - cacheWriteInputTokens)

-    const total = iife(() => {
-      // Anthropic doesn't provide total_tokens, also ai sdk will vastly undercount if we
-      // don't compute from components
-      if (
-        input.model.api.npm === "@ai-sdk/anthropic" ||
-        input.model.api.npm === "@ai-sdk/amazon-bedrock" ||
-        input.model.api.npm === "@ai-sdk/google-vertex/anthropic"
-      ) {
-        return adjustedInputTokens + outputTokens + cacheReadInputTokens + cacheWriteInputTokens
-      }
-      return input.usage.totalTokens
-    })
+    const total = input.usage.totalTokens

     const tokens = {
       total,

PATCH

echo "Patch applied successfully."
