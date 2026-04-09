#!/bin/bash
set -e

cd /workspace/continue

# Apply the gold patch for OpenRouter headers
patch -p1 << 'PATCH'
diff --git a/core/llm/llms/OpenRouter.ts b/core/llm/llms/OpenRouter.ts
index b277282458..0c389f7bd7 100644
--- a/core/llm/llms/OpenRouter.ts
+++ b/core/llm/llms/OpenRouter.ts
@@ -1,5 +1,7 @@
 import { ChatCompletionCreateParams } from "openai/resources/index";

+import { OPENROUTER_HEADERS } from "@continuedev/openai-adapters";
+
 import { LLMOptions } from "../../index.js";
 import { osModelsEditPrompt } from "../templates/edit.js";

@@ -18,6 +20,19 @@ class OpenRouter extends OpenAI {
     useLegacyCompletionsEndpoint: false,
   };

+  constructor(options: LLMOptions) {
+    super({
+      ...options,
+      requestOptions: {
+        ...options.requestOptions,
+        headers: {
+          ...OPENROUTER_HEADERS,
+          ...options.requestOptions?.headers,
+        },
+      },
+    });
+  }
+
   private isAnthropicModel(model?: string): boolean {
     if (!model) return false;
     const modelLower = model.toLowerCase();
diff --git a/packages/openai-adapters/src/apis/OpenRouter.ts b/packages/openai-adapters/src/apis/OpenRouter.ts
index 7c45fddeed..542699d20c 100644
--- a/packages/openai-adapters/src/apis/OpenRouter.ts
+++ b/packages/openai-adapters/src/apis/OpenRouter.ts
@@ -10,9 +10,10 @@ export interface OpenRouterConfig extends OpenAIConfig {

 // TODO: Extract detailed error info from OpenRouter's error.metadata.raw to surface better messages

-const OPENROUTER_HEADERS: Record<string, string> = {
+export const OPENROUTER_HEADERS: Record<string, string> = {
   "HTTP-Referer": "https://www.continue.dev/",
-  "X-Title": "Continue",
+  "X-OpenRouter-Title": "Continue",
+  "X-OpenRouter-Categories": "ide-extension",
 };

 export class OpenRouterApi extends OpenAIApi {
diff --git a/packages/openai-adapters/src/index.ts b/packages/openai-adapters/src/index.ts
index 467c7a71ae..c9eb4da00f 100644
--- a/packages/openai-adapters/src/index.ts
+++ b/packages/openai-adapters/src/index.ts
@@ -243,4 +243,5 @@ export {
 } from "./apis/AnthropicUtils.js";

 export { isResponsesModel } from "./apis/openaiResponses.js";
+export { OPENROUTER_HEADERS } from "./apis/OpenRouter.js";
 export { extractBase64FromDataUrl, parseDataUrl } from "./util/url.js";
PATCH

# Verify the patch was applied by checking for a distinctive line
if ! grep -q "X-OpenRouter-Categories" packages/openai-adapters/src/apis/OpenRouter.ts; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
