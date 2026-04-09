#!/bin/bash
set -euo pipefail

cd /workspace/continue

# Idempotency check: check if the patch has already been applied
if grep -q "the tool code block format shown below" core/tools/systemMessageTools/toolCodeblocks/index.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/core/tools/systemMessageTools/toolCodeblocks/index.ts b/core/tools/systemMessageTools/toolCodeblocks/index.ts
index a2cdc393d66..3acddb70f00 100644
--- a/core/tools/systemMessageTools/toolCodeblocks/index.ts
+++ b/core/tools/systemMessageTools/toolCodeblocks/index.ts
@@ -65,15 +65,15 @@ export class SystemMessageToolCodeblocksFramework
     return toolDefinition.trim();
   }

-  systemMessagePrefix = \`You have access to tools. To call a tool, you MUST respond with EXACTLY this format — a tool code block (\\\`\\\`\\\`tool) using the syntax shown below.
+  systemMessagePrefix = \`You have access to tools. To call a tool, you MUST respond with EXACTLY the tool code block format shown below.

 CRITICAL: Follow the exact syntax. Do not use XML tags, JSON objects, or any other format for tool calls.\`;

   systemMessageSuffix = \`RULES FOR TOOL USE:
-1. To call a tool, output a \\\`\\\`\\\`tool code block using EXACTLY the format shown above.
+1. To call a tool, output a tool code block using EXACTLY the format shown above.
 2. Always start the code block on a new line.
 3. You can only call ONE tool at a time.
-4. The \\\`\\\`\\\`tool code block MUST be the last thing in your response. Stop immediately after the closing \\\`\\\`\\\`.
+4. The tool code block MUST be the last thing in your response. Stop immediately after the closing fence.
 5. Do NOT wrap tool calls in XML tags like <tool_call> or <function=...>.
 6. Do NOT use JSON format for tool calls.
 7. Do NOT invent tools that are not listed above.
PATCH

echo "Patch applied successfully!"
