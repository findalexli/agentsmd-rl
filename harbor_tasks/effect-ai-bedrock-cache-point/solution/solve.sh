#!/bin/bash
set -euo pipefail

cd /workspace/effect

# Apply the gold patch
git apply <<'PATCH'
diff --git a/.changeset/tender-walls-act.md b/.changeset/tender-walls-act.md
new file mode 100644
index 00000000000..4c08d9c0082
--- /dev/null
+++ b/.changeset/tender-walls-act.md
@@ -0,0 +1,5 @@
+---
+"@effect/ai-amazon-bedrock": patch
+---
+
+fix cache point support for user and tool messages
diff --git a/packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts b/packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts
index fef36e59e4b..dbcadd08643 100644
--- a/packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts
+++ b/packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts
@@ -406,6 +406,10 @@ const prepareMessages: (options: LanguageModel.ProviderOptions) => Effect.Effect
                 break
               }
             }
+
+            if (getCachePoint(message)) {
+              content.push(BEDROCK_CACHE_POINT)
+            }
           }

           messages.push({ role: "user", content })
PATCH

# Verify patch applied
grep -q "if (getCachePoint(message))" packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts