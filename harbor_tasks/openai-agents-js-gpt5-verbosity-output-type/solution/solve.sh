#!/bin/bash
set -euo pipefail

cd /workspace/openai-agents-js

# Check idempotency — if fix already applied, skip
if grep -q "const { text, ...restOfProviderData } =" packages/agents-openai/src/openaiResponsesModel.ts; then
    echo "Fix already applied, skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/agents-openai/src/openaiResponsesModel.ts b/packages/agents-openai/src/openaiResponsesModel.ts
index f8ed1a11b..e21738974 100644
--- a/packages/agents-openai/src/openaiResponsesModel.ts
+++ b/packages/agents-openai/src/openaiResponsesModel.ts
@@ -71,12 +71,14 @@ function getToolChoice(

 function getResponseFormat(
   outputType: SerializedOutputType,
+  otherProperties: Record<string, any> | undefined,
 ): OpenAI.Responses.ResponseTextConfig | undefined {
   if (outputType === 'text') {
-    return undefined;
+    return otherProperties;
   }

   return {
+    ...otherProperties,
     format: outputType,
   };
 }
@@ -830,7 +832,9 @@ export class OpenAIResponsesModel implements Model {
     const input = getInputItems(request.input);
     const { tools, include } = getTools(request.tools, request.handoffs);
     const toolChoice = getToolChoice(request.modelSettings.toolChoice);
-    const responseFormat = getResponseFormat(request.outputType);
+    const { text, ...restOfProviderData } =
+      request.modelSettings.providerData ?? {};
+    const responseFormat = getResponseFormat(request.outputType, text);
     const prompt = getPrompt(request.prompt);

     let parallelToolCalls: boolean | undefined = undefined;
@@ -859,7 +863,7 @@ export class OpenAIResponsesModel implements Model {
       stream,
       text: responseFormat,
       store: request.modelSettings.store,
-      ...request.modelSettings.providerData,
+      ...restOfProviderData,
     };

     if (logger.dontLogModelData) {
PATCH

echo "Patch applied successfully."
