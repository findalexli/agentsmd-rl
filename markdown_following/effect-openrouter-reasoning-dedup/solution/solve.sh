#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

TARGET="packages/ai/openrouter/src/OpenRouterLanguageModel.ts"

if grep -q '} else if (Predicate.isNotNullable(delta.reasoning) && delta.reasoning.length > 0) {' "$TARGET"; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/whole-jokes-join.md b/.changeset/whole-jokes-join.md
new file mode 100644
index 00000000000..ce95d93a662
--- /dev/null
+++ b/.changeset/whole-jokes-join.md
@@ -0,0 +1,5 @@
+---
+"@effect/ai-openrouter": patch
+---
+
+fix(ai-openrouter): deduplicate reasoning parts when both `reasoning` and `reasoning_details` are present in a stream delta
diff --git a/packages/ai/openrouter/src/OpenRouterLanguageModel.ts b/packages/ai/openrouter/src/OpenRouterLanguageModel.ts
index 5fe725ba6f6..29acdc5ab95 100644
--- a/packages/ai/openrouter/src/OpenRouterLanguageModel.ts
+++ b/packages/ai/openrouter/src/OpenRouterLanguageModel.ts
@@ -796,10 +796,6 @@ const makeStreamResponse: (stream: Stream.Stream<ChatStreamingResponseChunk, AiE
           })
         }

-        if (Predicate.isNotNullable(delta.reasoning) && delta.reasoning.length > 0) {
-          emitReasoningPart(delta.reasoning)
-        }
-
         if (Predicate.isNotNullable(delta.reasoning_details) && delta.reasoning_details.length > 0) {
           for (const detail of delta.reasoning_details) {
             switch (detail.type) {
@@ -830,6 +826,8 @@ const makeStreamResponse: (stream: Stream.Stream<ChatStreamingResponseChunk, AiE
               }
             }
           }
+        } else if (Predicate.isNotNullable(delta.reasoning) && delta.reasoning.length > 0) {
+          emitReasoningPart(delta.reasoning)
         }

         // Text Parts
PATCH

echo "Patch applied."
