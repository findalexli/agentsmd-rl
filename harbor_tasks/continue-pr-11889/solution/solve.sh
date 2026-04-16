#!/bin/bash
set -e

cd /workspace/continue

# Apply the gold patch
git apply --ignore-whitespace <<'PATCH'
diff --git a/packages/openai-adapters/src/apis/OpenAI.ts b/packages/openai-adapters/src/apis/OpenAI.ts
index e41c590ecf..d0f8d30ca3 100644
--- a/packages/openai-adapters/src/apis/OpenAI.ts
+++ b/packages/openai-adapters/src/apis/OpenAI.ts
@@ -54,6 +54,16 @@ export class OpenAIApi implements BaseLlmApi {
      (body as any).stream_options = { include_usage: true };
    }

+    // DeepSeek reasoner models use max_completion_tokens instead of max_tokens
+    if (
+      body.max_tokens &&
+      (this.apiBase?.includes("api.deepseek.com") ||
+        body.model.includes("deepseek-reasoner"))
+    ) {
+      body.max_completion_tokens = body.max_tokens;
+      body.max_tokens = undefined;
+    }
+
     // o-series models - only apply for official OpenAI API
     const isOfficialOpenAIAPI = this.apiBase === "https://api.openai.com/v1/";
     if (isOfficialOpenAIAPI) {
PATCH

# Verify the patch was applied
grep -q "deepseek-reasoner" packages/openai-adapters/src/apis/OpenAI.ts