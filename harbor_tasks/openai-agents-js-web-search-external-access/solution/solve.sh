#!/usr/bin/env bash
# Apply the gold-fix patch for openai-agents-js#1140.
# Idempotent: re-runs are no-ops once the patch is in place.
set -euo pipefail

cd /workspace/openai-agents-js

# Distinctive line from the patch — fast idempotency check
if grep -q "external_web_access = options.externalWebAccess" \
        packages/agents-openai/src/tools.ts 2>/dev/null; then
    echo "[solve] gold patch already applied, skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/agents-openai/src/openaiResponsesModel.ts b/packages/agents-openai/src/openaiResponsesModel.ts
index 89a29d7ef..d6935ba9d 100644
--- a/packages/agents-openai/src/openaiResponsesModel.ts
+++ b/packages/agents-openai/src/openaiResponsesModel.ts
@@ -1514,13 +1514,20 @@ function converTool<_TContext = unknown>(
     };
   } else if (tool.type === 'hosted_tool') {
     if (tool.providerData?.type === 'web_search') {
+      const webSearchTool: OpenAI.Responses.WebSearchTool & {
+        external_web_access?: boolean;
+      } = {
+        type: 'web_search',
+        user_location: tool.providerData.user_location,
+        filters: tool.providerData.filters,
+        search_context_size: tool.providerData.search_context_size,
+      };
+      if (tool.providerData.external_web_access !== undefined) {
+        webSearchTool.external_web_access =
+          tool.providerData.external_web_access;
+      }
       return {
-        tool: {
-          type: 'web_search',
-          user_location: tool.providerData.user_location,
-          filters: tool.providerData.filters,
-          search_context_size: tool.providerData.search_context_size,
-        },
+        tool: webSearchTool,
         include: undefined,
       };
     } else if (tool.providerData?.type === 'web_search_preview') {
diff --git a/packages/agents-openai/src/tools.ts b/packages/agents-openai/src/tools.ts
index 5695e535f..0065c682f 100644
--- a/packages/agents-openai/src/tools.ts
+++ b/packages/agents-openai/src/tools.ts
@@ -55,6 +55,12 @@ export type WebSearchTool = {
    * search. One of `low`, `medium`, or `high`. `medium` is the default.
    */
   searchContextSize: 'low' | 'medium' | 'high';
+
+  /**
+   * Whether the tool may fetch live internet content. When omitted, the API
+   * default is used.
+   */
+  externalWebAccess?: boolean;
 };

 /**
@@ -74,6 +80,9 @@ export function webSearchTool(
       : undefined,
     search_context_size: options.searchContextSize ?? 'medium',
   };
+  if (options.externalWebAccess !== undefined) {
+    providerData.external_web_access = options.externalWebAccess;
+  }
   return {
     type: 'hosted_tool',
     name: options.name ?? 'web_search',
diff --git a/packages/agents-openai/src/types/providerData.ts b/packages/agents-openai/src/types/providerData.ts
index de54f23aa..d4eeff0af 100644
--- a/packages/agents-openai/src/types/providerData.ts
+++ b/packages/agents-openai/src/types/providerData.ts
@@ -3,6 +3,8 @@ import OpenAI from 'openai';
 export type WebSearchTool = Omit<OpenAI.Responses.WebSearchTool, 'type'> & {
   type: 'web_search';
   name: 'web_search' | 'web_search_preview' | (string & {});
+  // The Responses API supports this field, but openai-node typings do not expose it yet.
+  external_web_access?: boolean;
 };

 export type FileSearchTool = Omit<OpenAI.Responses.FileSearchTool, 'type'> & {
PATCH

echo "[solve] gold patch applied"
