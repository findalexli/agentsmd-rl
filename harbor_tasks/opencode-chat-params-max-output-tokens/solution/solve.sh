#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'params.maxOutputTokens' packages/opencode/src/session/llm.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/session/llm.ts b/packages/opencode/src/session/llm.ts
index 1813346cdc93..7ef6269b58d3 100644
--- a/packages/opencode/src/session/llm.ts
+++ b/packages/opencode/src/session/llm.ts
@@ -160,6 +160,11 @@ export namespace LLM {
             ...input.messages,
           ]

+    const maxOutputTokens =
+      isOpenaiOauth || provider.id.includes("github-copilot")
+        ? undefined
+        : ProviderTransform.maxOutputTokens(input.model)
+
     const params = await Plugin.trigger(
       "chat.params",
       {
@@ -175,6 +180,7 @@ export namespace LLM {
           : undefined,
         topP: input.agent.topP ?? ProviderTransform.topP(input.model),
         topK: ProviderTransform.topK(input.model),
+        maxOutputTokens,
         options,
       },
     )
@@ -193,11 +199,6 @@ export namespace LLM {
       },
     )

-    const maxOutputTokens =
-      isOpenaiOauth || provider.id.includes("github-copilot")
-        ? undefined
-        : ProviderTransform.maxOutputTokens(input.model)
-
     const tools = await resolveTools(input)

     // LiteLLM and some Anthropic proxies require the tools parameter to be present
@@ -291,7 +292,7 @@ export namespace LLM {
       activeTools: Object.keys(tools).filter((x) => x !== "invalid"),
       tools,
       toolChoice: input.toolChoice,
-      maxOutputTokens,
+      maxOutputTokens: params.maxOutputTokens,
       abortSignal: input.abort,
       headers: {
         ...(input.model.providerID.startsWith("opencode")

diff --git a/packages/plugin/src/index.ts b/packages/plugin/src/index.ts
index 473cac8a9bff..1afb55daa76e 100644
--- a/packages/plugin/src/index.ts
+++ b/packages/plugin/src/index.ts
@@ -212,7 +212,13 @@ export interface Hooks {
    */
   "chat.params"?: (
     input: { sessionID: string; agent: string; model: Model; provider: ProviderContext; message: UserMessage },
-    output: { temperature: number; topP: number; topK: number; options: Record<string, any> },
+    output: {
+      temperature: number
+      topP: number
+      topK: number
+      maxOutputTokens: number | undefined
+      options: Record<string, any>
+    },
   ) => Promise<void>
   "chat.headers"?: (
     input: { sessionID: string; agent: string; model: Model; provider: ProviderContext; message: UserMessage },

PATCH

echo "Patch applied successfully."
