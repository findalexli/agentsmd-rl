#!/bin/bash
set -euo pipefail

cd /workspace/openai-agents-js

if grep -q "getTextFromOutputMessage" packages/agents-core/src/utils/messages.ts 2>/dev/null; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/bright-fans-sing.md b/.changeset/bright-fans-sing.md
new file mode 100644
index 000000000..513dbad65
--- /dev/null
+++ b/.changeset/bright-fans-sing.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': patch
+---
+
+fix: recover segmented assistant output in agent tools and finalization
diff --git a/packages/agents-core/src/runner/turnResolution.ts b/packages/agents-core/src/runner/turnResolution.ts
index 788120e22..58fd96561 100644
--- a/packages/agents-core/src/runner/turnResolution.ts
+++ b/packages/agents-core/src/runner/turnResolution.ts
@@ -5,7 +5,7 @@ import { RunItem, RunMessageOutputItem, RunToolApprovalItem } from '../items';
 import { ModelResponse } from '../model';
 import type { Runner, ToolErrorFormatter } from '../run';
 import { RunState } from '../runState';
-import { getLastTextFromOutputMessage } from '../utils/messages';
+import { getTextFromOutputMessage } from '../utils/messages';
 import { getSchemaAndParserFromInputType } from '../utils/tools';
 import { safeExecute } from '../utils/safeExecute';
 import { addErrorToCurrentSpan } from '../tracing/context';
@@ -783,9 +783,7 @@ export async function resolveTurnAfterModelResponse<TContext>(
   // we will use the last content output as the final output
   const potentialFinalOutput =
     messageItems.length > 0
-      ? getLastTextFromOutputMessage(
-          messageItems[messageItems.length - 1].rawItem,
-        )
+      ? getTextFromOutputMessage(messageItems[messageItems.length - 1].rawItem)
       : undefined;

   // if there is no output we just run again
diff --git a/packages/agents-core/src/utils/messages.ts b/packages/agents-core/src/utils/messages.ts
index 043ee84af..532182a10 100644
--- a/packages/agents-core/src/utils/messages.ts
+++ b/packages/agents-core/src/utils/messages.ts
@@ -1,5 +1,20 @@
 import { ResponseOutputItem } from '../types';
 import { ModelResponse } from '../model';
+import type { AssistantMessageItem } from '../types/protocol';
+
+function getAssistantMessage(
+  outputMessage: ResponseOutputItem,
+): AssistantMessageItem | null {
+  if (outputMessage.type !== 'message') {
+    return null;
+  }
+
+  if (!('role' in outputMessage) || outputMessage.role !== 'assistant') {
+    return null;
+  }
+
+  return outputMessage as AssistantMessageItem;
+}

 /**
  * Get the last text from the output message.
@@ -9,20 +24,44 @@ import { ModelResponse } from '../model';
 export function getLastTextFromOutputMessage(
   outputMessage: ResponseOutputItem,
 ): string | undefined {
-  if (outputMessage.type !== 'message') {
+  const assistantMessage = getAssistantMessage(outputMessage);
+  if (!assistantMessage) {
     return undefined;
   }

-  if (outputMessage.role !== 'assistant') {
+  const lastItem =
+    assistantMessage.content[assistantMessage.content.length - 1];
+  if (lastItem.type !== 'output_text') {
     return undefined;
   }

-  const lastItem = outputMessage.content[outputMessage.content.length - 1];
-  if (lastItem.type !== 'output_text') {
+  return lastItem.text;
+}
+
+/**
+ * Get all text from the output message.
+ * @param outputMessage
+ * @returns
+ */
+export function getTextFromOutputMessage(
+  outputMessage: ResponseOutputItem,
+): string | undefined {
+  const assistantMessage = getAssistantMessage(outputMessage);
+  if (!assistantMessage) {
     return undefined;
   }

-  return lastItem.text;
+  let sawText = false;
+  const text = assistantMessage.content.reduce((acc, item) => {
+    if (item.type !== 'output_text') {
+      return acc;
+    }
+
+    sawText = true;
+    return acc + item.text;
+  }, '');
+
+  return sawText ? text : undefined;
 }

 /**
@@ -36,6 +75,6 @@ export function getOutputText(output: ModelResponse) {
   }

   return (
-    getLastTextFromOutputMessage(output.output[output.output.length - 1]) || ''
+    getTextFromOutputMessage(output.output[output.output.length - 1]) || ''
   );
 }
PATCH

echo "Patch applied successfully."
