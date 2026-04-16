#!/bin/bash
set -e

cd /workspace/continue

# Apply the fix for Moonshot reasoning_content field support
cat <<'PATCH' | git apply -
--- a/core/llm/llms/Moonshot.ts
+++ b/core/llm/llms/Moonshot.ts
@@ -6,6 +6,13 @@ import OpenAI from "./OpenAI.js";

 class Moonshot extends OpenAI {
   static providerName = "moonshot";
+
+  constructor(options: LLMOptions) {
+    super(options);
+    this.supportsReasoningContentField =
+      this.model?.startsWith("kimi") ?? false;
+  }
+
   static defaultOptions: Partial<LLMOptions> = {
     apiBase: "https://api.moonshot.cn/v1/",
     model: "moonshot-v1-8k",
PATCH

# Verify the patch was applied by checking for distinctive line
grep -q "this.supportsReasoningContentField" core/llm/llms/Moonshot.ts || exit 1

echo "Patch applied successfully"
