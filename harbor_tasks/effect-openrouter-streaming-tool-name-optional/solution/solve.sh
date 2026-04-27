#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

DISTINCTIVE='name: Schema.optionalWith(Schema.String, { nullable: true }),'
TARGET='packages/ai/openrouter/src/OpenRouterClient.ts'

if grep -F "${DISTINCTIVE}" "${TARGET}" >/dev/null 2>&1 \
    && grep -c "Schema.optionalWith(Schema.String" "${TARGET}" | awk '{exit !($1>=2)}'; then
    echo "[solve.sh] Patch already applied; skipping."
    exit 0
fi

git apply <<'PATCH'
diff --git a/.changeset/fix-streaming-tool-call-schema.md b/.changeset/fix-streaming-tool-call-schema.md
new file mode 100644
index 00000000000..fc878598c88
--- /dev/null
+++ b/.changeset/fix-streaming-tool-call-schema.md
@@ -0,0 +1,9 @@
+---
+"@effect/ai-openrouter": patch
+---
+
+Fix `ChatStreamingMessageToolCall` schema rejecting valid streaming tool call chunks.
+
+The OpenAI streaming spec splits tool calls across multiple SSE chunks — `function.name` is only present on the first chunk, but the schema required it on every chunk, causing a `MalformedOutput` error whenever the model returned a tool call.
+
+Made `function.name` optional to match `id` which was already optional.
diff --git a/packages/ai/openrouter/src/OpenRouterClient.ts b/packages/ai/openrouter/src/OpenRouterClient.ts
index ec61801571f..aa9792b77ab 100644
--- a/packages/ai/openrouter/src/OpenRouterClient.ts
+++ b/packages/ai/openrouter/src/OpenRouterClient.ts
@@ -315,7 +315,7 @@ export class ChatStreamingMessageToolCall extends Schema.Class<ChatStreamingMess
   id: Schema.optionalWith(Schema.String, { nullable: true }),
   type: Schema.Literal("function"),
   function: Schema.Struct({
-    name: Schema.String,
+    name: Schema.optionalWith(Schema.String, { nullable: true }),
     arguments: Schema.String
   })
 }) {}
PATCH

echo "[solve.sh] Patch applied."
