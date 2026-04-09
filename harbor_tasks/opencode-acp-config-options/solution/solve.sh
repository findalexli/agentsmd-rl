#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'function buildConfigOptions' packages/opencode/src/acp/agent.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/acp/agent.ts b/packages/opencode/src/acp/agent.ts
index 96a97be75296..6e87e7642d65 100644
--- a/packages/opencode/src/acp/agent.ts
+++ b/packages/opencode/src/acp/agent.ts
@@ -21,6 +21,9 @@ import {
   type Role,
   type SessionInfo,
   type SetSessionModelRequest,
+  type SessionConfigOption,
+  type SetSessionConfigOptionRequest,
+  type SetSessionConfigOptionResponse,
   type SetSessionModeRequest,
   type SetSessionModeResponse,
   type ToolCallContent,
@@ -601,6 +604,7 @@ export namespace ACP {

         return {
           sessionId,
+          configOptions: load.configOptions,
           models: load.models,
           modes: load.modes,
           _meta: load._meta,
@@ -660,6 +664,11 @@ export namespace ACP {
             result.modes.currentModeId = lastUser.agent
             this.sessionManager.setMode(sessionId, lastUser.agent)
           }
+          result.configOptions = buildConfigOptions({
+            currentModelId: result.models.currentModelId,
+            availableModels: result.models.availableModels,
+            modes: result.modes,
+          })
         }

         for (const msg of messages ?? []) {
@@ -1266,6 +1275,11 @@ export namespace ACP {
           availableModels,
         },
         modes,
+        configOptions: buildConfigOptions({
+          currentModelId: formatModelIdWithVariant(model, currentVariant, availableVariants, true),
+          availableModels,
+          modes,
+        }),
         _meta: buildVariantMeta({
           model,
           variant: this.sessionManager.getVariant(sessionId),
@@ -1305,6 +1319,44 @@ export namespace ACP {
       this.sessionManager.setMode(params.sessionId, params.modeId)
     }

+    async setSessionConfigOption(params: SetSessionConfigOptionRequest): Promise<SetSessionConfigOptionResponse> {
+      const session = this.sessionManager.get(params.sessionId)
+      const providers = await this.sdk.config
+        .providers({ directory: session.cwd }, { throwOnError: true })
+        .then((x) => x.data!.providers)
+      const entries = sortProvidersByName(providers)
+
+      if (params.configId === "model") {
+        if (typeof params.value !== "string") throw RequestError.invalidParams("model value must be a string")
+        const selection = parseModelSelection(params.value, providers)
+        this.sessionManager.setModel(session.id, selection.model)
+        this.sessionManager.setVariant(session.id, selection.variant)
+      } else if (params.configId === "mode") {
+        if (typeof params.value !== "string") throw RequestError.invalidParams("mode value must be a string")
+        const availableModes = await this.loadAvailableModes(session.cwd)
+        if (!availableModes.some((mode) => mode.id === params.value)) {
+          throw RequestError.invalidParams(JSON.stringify({ error: `Mode not found: ${params.value}` }))
+        }
+        this.sessionManager.setMode(session.id, params.value)
+      } else {
+        throw RequestError.invalidParams(JSON.stringify({ error: `Unknown config option: ${params.configId}` }))
+      }
+
+      const updatedSession = this.sessionManager.get(session.id)
+      const model = updatedSession.model ?? (await defaultModel(this.config, session.cwd))
+      const availableVariants = modelVariantsFromProviders(entries, model)
+      const currentModelId = formatModelIdWithVariant(model, updatedSession.variant, availableVariants, true)
+      const availableModels = buildAvailableModels(entries, { includeVariants: true })
+      const modeState = await this.resolveModeState(session.cwd, session.id)
+      const modes = modeState.currentModeId
+        ? { availableModes: modeState.availableModes, currentModeId: modeState.currentModeId }
+        : undefined
+
+      return {
+        configOptions: buildConfigOptions({ currentModelId, availableModels, modes }),
+      }
+    }
+
     async prompt(params: PromptRequest) {
       const sessionID = params.sessionId
       const session = this.sessionManager.get(sessionID)
@@ -1760,4 +1812,36 @@ export namespace ACP {

     return { model: parsed, variant: undefined }
   }
+
+  function buildConfigOptions(input: {
+    currentModelId: string
+    availableModels: ModelOption[]
+    modes?: { availableModes: ModeOption[]; currentModeId: string } | undefined
+  }): SessionConfigOption[] {
+    const options: SessionConfigOption[] = [
+      {
+        id: "model",
+        name: "Model",
+        category: "model",
+        type: "select",
+        currentValue: input.currentModelId,
+        options: input.availableModels.map((m) => ({ value: m.modelId, name: m.name })),
+      },
+    ]
+    if (input.modes) {
+      options.push({
+        id: "mode",
+        name: "Session Mode",
+        category: "mode",
+        type: "select",
+        currentValue: input.modes.currentModeId,
+        options: input.modes.availableModes.map((m) => ({
+          value: m.id,
+          name: m.name,
+          ...(m.description ? { description: m.description } : {}),
+        })),
+      })
+    }
+    return options
+  }
 }

PATCH

echo "Patch applied successfully."
