#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

# Fix index.ts: use ctx.provider instead of hardcoded "google"
sed -i 's/resolveGoogle31ForwardCompatModel({ providerId: "google", ctx })/resolveGoogle31ForwardCompatModel({\n          providerId: ctx.provider,\n          templateProviderId: GOOGLE_GEMINI_CLI_PROVIDER_ID,\n          ctx,\n        })/' extensions/google/index.ts

# Fix provider-models.ts: add flash-lite prefix, templateProviderId, and helper
cd /workspace/openclaw
git apply --whitespace=fix - << 'PATCH'
diff --git a/extensions/google/provider-models.ts b/extensions/google/provider-models.ts
index 9720c25de8c7..8c64a7539504 100644
--- a/extensions/google/provider-models.ts
+++ b/extensions/google/provider-models.ts
@@ -5,12 +5,51 @@ import type {
 import { cloneFirstTemplateModel } from "openclaw/plugin-sdk/provider-model-shared";

 const GEMINI_3_1_PRO_PREFIX = "gemini-3.1-pro";
+const GEMINI_3_1_FLASH_LITE_PREFIX = "gemini-3.1-flash-lite";
 const GEMINI_3_1_FLASH_PREFIX = "gemini-3.1-flash";
 const GEMINI_3_1_PRO_TEMPLATE_IDS = ["gemini-3-pro-preview"] as const;
+const GEMINI_3_1_FLASH_LITE_TEMPLATE_IDS = [
+  "gemini-3.1-flash-lite-preview",
+] as const;
 const GEMINI_3_1_FLASH_TEMPLATE_IDS = ["gemini-3-flash-preview"] as const;

+function cloneFirstGoogleTemplateModel(params: {
+  providerId: string;
+  templateProviderId?: string;
+  modelId: string;
+  templateIds: readonly string[];
+  ctx: ProviderResolveDynamicModelContext;
+  patch?: Partial<ProviderRuntimeModel>;
+}): ProviderRuntimeModel | undefined {
+  const templateProviderIds = [
+    params.providerId,
+    params.templateProviderId,
+  ]
+    .map((providerId) => providerId?.trim())
+    .filter((providerId): providerId is string => Boolean(providerId));
+
+  for (const templateProviderId of new Set(templateProviderIds)) {
+    const model = cloneFirstTemplateModel({
+      providerId: templateProviderId,
+      modelId: params.modelId,
+      templateIds: params.templateIds,
+      ctx: params.ctx,
+      patch: {
+        ...params.patch,
+        provider: params.providerId,
+      },
+    });
+    if (model) {
+      return model;
+    }
+  }
+
+  return undefined;
+}
+
 export function resolveGoogle31ForwardCompatModel(params: {
   providerId: string;
+  templateProviderId?: string;
   ctx: ProviderResolveDynamicModelContext;
 }): ProviderRuntimeModel | undefined {
   const trimmed = params.ctx.modelId.trim();
@@ -19,14 +58,17 @@ export function resolveGoogle31ForwardCompatModel(params: {
   let templateIds: readonly string[];
   if (lower.startsWith(GEMINI_3_1_PRO_PREFIX)) {
     templateIds = GEMINI_3_1_PRO_TEMPLATE_IDS;
+  } else if (lower.startsWith(GEMINI_3_1_FLASH_LITE_PREFIX)) {
+    templateIds = GEMINI_3_1_FLASH_LITE_TEMPLATE_IDS;
   } else if (lower.startsWith(GEMINI_3_1_FLASH_PREFIX)) {
     templateIds = GEMINI_3_1_FLASH_TEMPLATE_IDS;
   } else {
     return undefined;
   }

-  return cloneFirstTemplateModel({
+  return cloneFirstGoogleTemplateModel({
     providerId: params.providerId,
+    templateProviderId: params.templateProviderId,
     modelId: trimmed,
     templateIds,
     ctx: params.ctx,

PATCH
