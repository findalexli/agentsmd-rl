#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/effect
cd "$REPO"

DISTINCTIVE='Schema.optionalWith(Schema.Literal("function"), { nullable: true })'
TARGET='packages/ai/openrouter/src/OpenRouterClient.ts'

if grep -qF "$DISTINCTIVE" "$TARGET"; then
  echo "Patch already applied; skipping."
  exit 0
fi

patch -p1 <<'PATCH'
--- a/packages/ai/openrouter/src/OpenRouterClient.ts
+++ b/packages/ai/openrouter/src/OpenRouterClient.ts
@@ -313,10 +313,10 @@ export class ChatStreamingMessageToolCall extends Schema.Class<ChatStreamingMess
 )({
   index: Schema.Number,
   id: Schema.optionalWith(Schema.String, { nullable: true }),
-  type: Schema.Literal("function"),
+  type: Schema.optionalWith(Schema.Literal("function"), { nullable: true }),
   function: Schema.Struct({
     name: Schema.optionalWith(Schema.String, { nullable: true }),
-    arguments: Schema.String
+    arguments: Schema.optionalWith(Schema.String, { nullable: true })
   })
 }) {}
PATCH

echo "Patch applied."
