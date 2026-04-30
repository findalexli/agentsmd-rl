#!/usr/bin/env bash
# Oracle solution: applies the gold patch from openai/openai-agents-js#1129.
# This is the inlined gold diff. Do NOT fetch from GitHub or any other source.
set -euo pipefail

cd /workspace/openai-agents-js

DISTINCTIVE='The live API rejects empty pending_safety_checks on replayed computer calls.'
if grep -F -q "$DISTINCTIVE" packages/agents-openai/src/openaiResponsesModel.ts; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/agents-openai/src/openaiResponsesModel.ts b/packages/agents-openai/src/openaiResponsesModel.ts
index 077d37141..89a29d7ef 100644
--- a/packages/agents-openai/src/openaiResponsesModel.ts
+++ b/packages/agents-openai/src/openaiResponsesModel.ts
@@ -2057,8 +2057,6 @@ function getInputItems(
       const pendingSafetyChecks = getProviderDataField<
         OpenAI.Responses.ResponseComputerToolCall['pending_safety_checks']
       >(item.providerData, ['pendingSafetyChecks', 'pending_safety_checks']);
-      const normalizedPendingSafetyChecks: OpenAI.Responses.ResponseComputerToolCall['pending_safety_checks'] =
-        Array.isArray(pendingSafetyChecks) ? pendingSafetyChecks : [];
       const batchedActions = Array.isArray(
         (item as { actions?: unknown }).actions,
       )
@@ -2074,12 +2072,15 @@ function getInputItems(
           : item.action
             ? { action: item.action }
             : {};
-      const entry: OpenAI.Responses.ResponseComputerToolCall = {
+      // The live API rejects empty pending_safety_checks on replayed computer calls.
+      const entry = {
         type: 'computer_call',
         call_id: item.callId,
         id: item.id!,
         status: item.status,
-        pending_safety_checks: normalizedPendingSafetyChecks,
+        ...(Array.isArray(pendingSafetyChecks) && pendingSafetyChecks.length > 0
+          ? { pending_safety_checks: pendingSafetyChecks }
+          : {}),
         ...actionPayload,
         ...getSnakeCasedProviderDataWithoutReservedKeys(item.providerData, [
           'type',
@@ -2092,7 +2093,7 @@ function getInputItems(
         ]),
       };

-      return entry;
+      return entry as unknown as OpenAI.Responses.ResponseComputerToolCall;
     }

     if (item.type === 'computer_call_result') {
@@ -2108,9 +2109,10 @@ function getInputItems(
         call_id: item.callId,
         output: buildResponseOutput(item),
         status: item.providerData?.status,
-        acknowledged_safety_checks: Array.isArray(acknowledgedSafetyChecks)
-          ? acknowledgedSafetyChecks
-          : [],
+        ...(Array.isArray(acknowledgedSafetyChecks) &&
+        acknowledgedSafetyChecks.length > 0
+          ? { acknowledged_safety_checks: acknowledgedSafetyChecks }
+          : {}),
         ...getSnakeCasedProviderDataWithoutReservedKeys(item.providerData, [
           'type',
           'id',
PATCH

echo "Gold patch applied."
