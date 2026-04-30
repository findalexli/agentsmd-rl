#!/bin/bash
set -e
cd /workspace/effect

# Apply the gold fix: make function.name optional in ChatStreamingMessageToolCall
cat <<'PATCH' | git apply --verbose -
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

# Verify the fix was applied
grep -q 'name: Schema.optionalWith' packages/ai/openrouter/src/OpenRouterClient.ts || {
  echo "ERROR: Patch did not apply correctly"
  exit 1
}

echo "Fix applied successfully."
