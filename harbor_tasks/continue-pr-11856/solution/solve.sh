#!/bin/bash
set -e
cd /workspace/continue

# Idempotency check - if the fix is already applied, skip
if grep -q 'google/gemini-3' core/llm/toolSupport.ts 2>/dev/null; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch
git fetch origin main --filter=blob:none 2>/dev/null || true

cat <<'PATCH' | git apply -
diff --git a/core/autocomplete/CompletionProvider.ts b/core/autocomplete/CompletionProvider.ts
index 27e7ad53723..d4aba5fbc8d 100644
--- a/core/autocomplete/CompletionProvider.ts
+++ b/core/autocomplete/CompletionProvider.ts
@@ -89,7 +89,7 @@ export class CompletionProvider {
       llm.completionOptions.temperature = 0.01;
     }

-    if (llm instanceof OpenAI) {
+    if (llm instanceof OpenAI && llm.providerName !== "openrouter") {
       llm.useLegacyCompletionsEndpoint = true;
     }

diff --git a/core/llm/llms/OpenRouter.ts b/core/llm/llms/OpenRouter.ts
index 4672a465897..b2772824583 100644
--- a/core/llm/llms/OpenRouter.ts
+++ b/core/llm/llms/OpenRouter.ts
@@ -18,18 +18,52 @@ class OpenRouter extends OpenAI {
     useLegacyCompletionsEndpoint: false,
   };

-  /**
-   * Detect if the model is an Anthropic/Claude model
-   */
   private isAnthropicModel(model?: string): boolean {
     if (!model) return false;
     const modelLower = model.toLowerCase();
     return modelLower.includes("claude");
   }

+  private isGeminiModel(model?: string): boolean {
+    if (!model) return false;
+    return model.toLowerCase().startsWith("google/");
+  }
+
   /**
-   * Add cache_control to message content for Anthropic models
+   * Add thought_signature fallback to Gemini tool calls that don't already
+   * have one, preventing 400 errors from missing thought_signature.
+   * See: https://ai.google.dev/gemini-api/docs/thought-signatures
    */
+  private addGeminiThoughtSignatures(
+    body: ChatCompletionCreateParams,
+  ): ChatCompletionCreateParams {
+    body.messages = body.messages.map((message: any) => {
+      if (message.role === "assistant" && message.tool_calls?.length) {
+        return {
+          ...message,
+          tool_calls: message.tool_calls.map((toolCall: any, index: number) => {
+            if (index !== 0) return toolCall;
+            if (toolCall.extra_content?.google?.thought_signature) {
+              return toolCall;
+            }
+            return {
+              ...toolCall,
+              extra_content: {
+                ...toolCall.extra_content,
+                google: {
+                  ...toolCall.extra_content?.google,
+                  thought_signature: "skip_thought_signature_validator",
+                },
+              },
+            };
+          }),
+        };
+      }
+      return message;
+    });
+    return body;
+  }
+
   private addCacheControlToContent(content: any, addCaching: boolean): any {
     if (!addCaching) return content;

@@ -59,16 +93,15 @@ class OpenRouter extends OpenAI {
     return content;
   }

-  /**
-   * Override modifyChatBody to add Anthropic caching when appropriate
-   */
   protected modifyChatBody(
     body: ChatCompletionCreateParams,
   ): ChatCompletionCreateParams {
-    // First apply parent modifications
     body = super.modifyChatBody(body);

-    // Check if we should apply Anthropic caching
+    if (this.isGeminiModel(body.model)) {
+      body = this.addGeminiThoughtSignatures(body);
+    }
+
     if (
       !this.isAnthropicModel(body.model) ||
       (!this.cacheBehavior && !this.completionOptions.promptCaching)
diff --git a/core/llm/toolSupport.test.ts b/core/llm/toolSupport.test.ts
index 2ecb72cad48..00ee1c30ec5 100644
--- a/core/llm/toolSupport.test.ts
+++ b/core/llm/toolSupport.test.ts
@@ -388,9 +388,35 @@ describe("PROVIDER_TOOL_SUPPORT", () => {
     const supportsFn = PROVIDER_TOOL_SUPPORT["openrouter"];

     it("should return false for moonshotai/kimi-k2:free model", () => {
-      // This fixes issue #6619
       expect(supportsFn("moonshotai/kimi-k2:free")).toBe(false);
     });
+
+    it("should return true for supported prefixes", () => {
+      expect(supportsFn("openai/gpt-4o")).toBe(true);
+      expect(supportsFn("anthropic/claude-sonnet-4")).toBe(true);
+      expect(supportsFn("google/gemini-2-flash")).toBe(true);
+      expect(supportsFn("google/gemini-3-pro-preview")).toBe(true);
+      expect(supportsFn("deepseek/deepseek-r1")).toBe(true);
+      expect(supportsFn("qwen/qwen3-coder-30b")).toBe(true);
+      expect(supportsFn("meta-llama/llama-4-scout")).toBe(true);
+    });
+
+    it("should strip :free/:extended/:beta suffixes before matching", () => {
+      expect(supportsFn("meta-llama/llama-3.2-3b-instruct:free")).toBe(true);
+      expect(supportsFn("deepseek/deepseek-r1:extended")).toBe(true);
+      expect(supportsFn("qwen/qwen3-coder:beta")).toBe(true);
+    });
+
+    it("should return false for unsupported models", () => {
+      expect(supportsFn("unknown/random-model")).toBe(false);
+      expect(supportsFn("some-provider/vision-model")).toBe(false);
+    });
+
+    it("should return false for excluded model patterns", () => {
+      expect(supportsFn("some/vision-model")).toBe(false);
+      expect(supportsFn("some/math-model")).toBe(false);
+      expect(supportsFn("some/guard-model")).toBe(false);
+    });
   });

   describe("edge cases", () => {
diff --git a/core/llm/toolSupport.ts b/core/llm/toolSupport.ts
index 8c309b1c394..4635d029380 100644
--- a/core/llm/toolSupport.ts
+++ b/core/llm/toolSupport.ts
@@ -318,9 +318,13 @@ export const PROVIDER_TOOL_SUPPORT: Record<string, (model: string) => boolean> =
         return false;
       }

+      const baseModel = model
+        .toLowerCase()
+        .replace(/:(free|extended|beta)$/, "");
+
       if (
         ["vision", "math", "guard", "mistrallite", "mistral-openorca"].some(
-          (part) => model.toLowerCase().includes(part),
+          (part) => baseModel.includes(part),
         )
       ) {
         return false;
@@ -339,6 +343,7 @@ export const PROVIDER_TOOL_SUPPORT: Record<string, (model: string) => boolean> =
         "microsoft/phi-3",
         "google/gemini-flash-1.5",
         "google/gemini-2",
+        "google/gemini-3",
         "google/gemini-pro",
         "x-ai/grok",
         "qwen/qwen3",
@@ -366,7 +371,7 @@ export const PROVIDER_TOOL_SUPPORT: Record<string, (model: string) => boolean> =
         "zai-org/glm",
       ];
       for (const prefix of supportedPrefixes) {
-        if (model.toLowerCase().startsWith(prefix)) {
+        if (baseModel.startsWith(prefix)) {
           return true;
         }
       }
@@ -382,14 +387,14 @@ export const PROVIDER_TOOL_SUPPORT: Record<string, (model: string) => boolean> =
         "moonshotai/kimi-k2",
       ];
       for (const specificModel of specificModels) {
-        if (model.toLowerCase() === specificModel) {
+        if (baseModel === specificModel) {
           return true;
         }
       }

       const supportedContains = ["llama-3.1"];
       for (const contained of supportedContains) {
-        if (model.toLowerCase().includes(contained)) {
+        if (baseModel.includes(contained)) {
           return true;
         }
       }
diff --git a/core/nextEdit/NextEditProvider.ts b/core/nextEdit/NextEditProvider.ts
index f92804a6c63..754f168c3c8 100644
--- a/core/nextEdit/NextEditProvider.ts
+++ b/core/nextEdit/NextEditProvider.ts
@@ -153,7 +153,7 @@ export class NextEditProvider {
       llm.completionOptions.temperature = 0.01;
     }

-    if (llm instanceof OpenAI) {
+    if (llm instanceof OpenAI && llm.providerName !== "openrouter") {
       llm.useLegacyCompletionsEndpoint = true;
     }
     // TODO: Resolve import error with TRIAL_FIM_MODEL
diff --git a/packages/openai-adapters/src/apis/OpenRouter.ts b/packages/openai-adapters/src/apis/OpenRouter.ts
index d6227affb2e..7c45fddeed6 100644
--- a/packages/openai-adapters/src/apis/OpenRouter.ts
+++ b/packages/openai-adapters/src/apis/OpenRouter.ts
@@ -8,6 +8,8 @@ export interface OpenRouterConfig extends OpenAIConfig {
   cachingStrategy?: import("./AnthropicCachingStrategies.js").CachingStrategyName;
 }

+// TODO: Extract detailed error info from OpenRouter's error.metadata.raw to surface better messages
+
 const OPENROUTER_HEADERS: Record<string, string> = {
   "HTTP-Referer": "https://www.continue.dev/",
   "X-Title": "Continue",
PATCH

echo "Gold patch applied successfully"