#!/bin/bash
set -e

cd /workspace/continue

# Check if already applied
if grep -q "supportsReasoningContentField" core/llm/llms/Moonshot.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
patch -p1 <<'PATCH'
diff --git a/core/llm/llms/Moonshot.ts b/core/llm/llms/Moonshot.ts
index 2235b5ac2cf..966aeb02efc 100644
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

echo "Patch applied successfully"
