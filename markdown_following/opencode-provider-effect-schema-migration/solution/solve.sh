#!/bin/bash
# Apply the gold patch from anomalyco/opencode#24027:
# refactor(provider): migrate provider domain to Effect Schema

set -euo pipefail

cd /workspace/opencode

# Idempotency: skip if already applied
if grep -q 'export const OauthMissing = namedSchemaError("ProviderAuthOauthMissing"' \
   packages/opencode/src/provider/auth.ts 2>/dev/null; then
  echo "Gold patch already applied — skipping."
  exit 0
fi

PATCH_FILE=$(mktemp)
cat > "$PATCH_FILE" <<'PATCH_EOF'
diff --git a/packages/opencode/specs/effect/schema.md b/packages/opencode/specs/effect/schema.md
index 0abdd9ed66a8..0d451f4a99ec 100644
--- a/packages/opencode/specs/effect/schema.md
+++ b/packages/opencode/specs/effect/schema.md
@@ -274,9 +274,9 @@ Possible later tightening after the Schema-first migration is stable:
 
 ### Provider domain
 
-- [ ] `src/provider/auth.ts`
-- [ ] `src/provider/models.ts`
-- [ ] `src/provider/provider.ts`
+- [x] `src/provider/auth.ts`
+- [x] `src/provider/models.ts`
+- [x] `src/provider/provider.ts`
 
 ### Tool schemas
 
diff --git a/packages/opencode/src/provider/auth.ts b/packages/opencode/src/provider/auth.ts
index 5d8b2765decc..0b4ac995a848 100644
--- a/packages/opencode/src/provider/auth.ts
+++ b/packages/opencode/src/provider/auth.ts
@@ -1,13 +1,12 @@
 import type { AuthOAuthResult, Hooks } from "@opencode-ai/plugin"
-import { NamedError } from "@opencode-ai/shared/util/error"
 import { Auth } from "@/auth"
 import { InstanceState } from "@/effect"
 import { zod } from "@/util/effect-zod"
+import { namedSchemaError } from "@/util/named-schema-error"
 import { withStatics } from "@/util/schema"
 import { Plugin } from "../plugin"
 import { ProviderID } from "./schema"
 import { Array as Arr, Effect, Layer, Record, Result, Context, Schema } from "effect"
-import z from "zod"
 
 const When = Schema.Struct({
   key: Schema.String,
@@ -70,22 +69,16 @@ export const CallbackInput = Schema.Struct({
 }).pipe(withStatics((s) => ({ zod: zod(s) })))
 export type CallbackInput = Schema.Schema.Type<typeof CallbackInput>
 
-export const OauthMissing = NamedError.create("ProviderAuthOauthMissing", z.object({ providerID: ProviderID.zod }))
+export const OauthMissing = namedSchemaError("ProviderAuthOauthMissing", { providerID: ProviderID })
 
-export const OauthCodeMissing = NamedError.create(
-  "ProviderAuthOauthCodeMissing",
-  z.object({ providerID: ProviderID.zod }),
-)
+export const OauthCodeMissing = namedSchemaError("ProviderAuthOauthCodeMissing", { providerID: ProviderID })
 
-export const OauthCallbackFailed = NamedError.create("ProviderAuthOauthCallbackFailed", z.object({}))
+export const OauthCallbackFailed = namedSchemaError("ProviderAuthOauthCallbackFailed", {})
 
-export const ValidationFailed = NamedError.create(
-  "ProviderAuthValidationFailed",
-  z.object({
-    field: z.string(),
-    message: z.string(),
-  }),
-)
+export const ValidationFailed = namedSchemaError("ProviderAuthValidationFailed", {
+  field: Schema.String,
+  message: Schema.String,
+})
 
 export type Error =
   | Auth.AuthError
diff --git a/packages/opencode/src/provider/models.ts b/packages/opencode/src/provider/models.ts
index 2924666c0ec5..36c4d8c23c61 100644
--- a/packages/opencode/src/provider/models.ts
+++ b/packages/opencode/src/provider/models.ts
@@ -1,7 +1,7 @@
 import { Global } from "../global"
 import { Log } from "../util"
 import path from "path"
-import z from "zod"
+import { Schema } from "effect"
 import { Installation } from "../installation"
 import { Flag } from "../flag/flag"
 import { lazy } from "@/util/lazy"
@@ -21,91 +21,85 @@ const filepath = path.join(
 )
 const ttl = 5 * 60 * 1000
 
-type JsonValue = string | number | boolean | null | { [key: string]: JsonValue } | JsonValue[]
-
-const JsonValue: z.ZodType<JsonValue> = z.lazy(() =>
-  z.union([z.string(), z.number(), z.boolean(), z.null(), z.array(JsonValue), z.record(z.string(), JsonValue)]),
-)
-
-const Cost = z.object({
-  input: z.number(),
-  output: z.number(),
-  cache_read: z.number().optional(),
-  cache_write: z.number().optional(),
-  context_over_200k: z
-    .object({
-      input: z.number(),
-      output: z.number(),
-      cache_read: z.number().optional(),
-      cache_write: z.number().optional(),
-    })
-    .optional(),
+const Cost = Schema.Struct({
+  input: Schema.Number,
+  output: Schema.Number,
+  cache_read: Schema.optional(Schema.Number),
+  cache_write: Schema.optional(Schema.Number),
+  context_over_200k: Schema.optional(
+    Schema.Struct({
+      input: Schema.Number,
+      output: Schema.Number,
+      cache_read: Schema.optional(Schema.Number),
+      cache_write: Schema.optional(Schema.Number),
+    }),
+  ),
 })
 
-export const Model = z.object({
-  id: z.string(),
-  name: z.string(),
-  family: z.string().optional(),
-  release_date: z.string(),
-  attachment: z.boolean(),
-  reasoning: z.boolean(),
-  temperature: z.boolean(),
-  tool_call: z.boolean(),
-  interleaved: z
-    .union([
-      z.literal(true),
-      z
-        .object({
-          field: z.enum(["reasoning_content", "reasoning_details"]),
-        })
-        .strict(),
-    ])
-    .optional(),
-  cost: Cost.optional(),
-  limit: z.object({
-    context: z.number(),
-    input: z.number().optional(),
-    output: z.number(),
+export const Model = Schema.Struct({
+  id: Schema.String,
+  name: Schema.String,
+  family: Schema.optional(Schema.String),
+  release_date: Schema.String,
+  attachment: Schema.Boolean,
+  reasoning: Schema.Boolean,
+  temperature: Schema.Boolean,
+  tool_call: Schema.Boolean,
+  interleaved: Schema.optional(
+    Schema.Union([
+      Schema.Literal(true),
+      Schema.Struct({
+        field: Schema.Literals(["reasoning_content", "reasoning_details"]),
+      }),
+    ]),
+  ),
+  cost: Schema.optional(Cost),
+  limit: Schema.Struct({
+    context: Schema.Number,
+    input: Schema.optional(Schema.Number),
+    output: Schema.Number,
   }),
-  modalities: z
-    .object({
-      input: z.array(z.enum(["text", "audio", "image", "video", "pdf"])),
-      output: z.array(z.enum(["text", "audio", "image", "video", "pdf"])),
-    })
-    .optional(),
-  experimental: z
-    .object({
-      modes: z
-        .record(
-          z.string(),
-          z.object({
-            cost: Cost.optional(),
-            provider: z
-              .object({
-                body: z.record(z.string(), JsonValue).optional(),
-                headers: z.record(z.string(), z.string()).optional(),
-              })
-              .optional(),
+  modalities: Schema.optional(
+    Schema.Struct({
+      input: Schema.Array(Schema.Literals(["text", "audio", "image", "video", "pdf"])),
+      output: Schema.Array(Schema.Literals(["text", "audio", "image", "video", "pdf"])),
+    }),
+  ),
+  experimental: Schema.optional(
+    Schema.Struct({
+      modes: Schema.optional(
+        Schema.Record(
+          Schema.String,
+          Schema.Struct({
+            cost: Schema.optional(Cost),
+            provider: Schema.optional(
+              Schema.Struct({
+                body: Schema.optional(Schema.Record(Schema.String, Schema.MutableJson)),
+                headers: Schema.optional(Schema.Record(Schema.String, Schema.String)),
+              }),
+            ),
           }),
-        )
-        .optional(),
-    })
-    .optional(),
-  status: z.enum(["alpha", "beta", "deprecated"]).optional(),
-  provider: z.object({ npm: z.string().optional(), api: z.string().optional() }).optional(),
+        ),
+      ),
+    }),
+  ),
+  status: Schema.optional(Schema.Literals(["alpha", "beta", "deprecated"])),
+  provider: Schema.optional(
+    Schema.Struct({ npm: Schema.optional(Schema.String), api: Schema.optional(Schema.String) }),
+  ),
 })
-export type Model = z.infer<typeof Model>
-
-export const Provider = z.object({
-  api: z.string().optional(),
-  name: z.string(),
-  env: z.array(z.string()),
-  id: z.string(),
-  npm: z.string().optional(),
-  models: z.record(z.string(), Model),
+export type Model = Schema.Schema.Type<typeof Model>
+
+export const Provider = Schema.Struct({
+  api: Schema.optional(Schema.String),
+  name: Schema.String,
+  env: Schema.Array(Schema.String),
+  id: Schema.String,
+  npm: Schema.optional(Schema.String),
+  models: Schema.Record(Schema.String, Model),
 })
 
-export type Provider = z.infer<typeof Provider>
+export type Provider = Schema.Schema.Type<typeof Provider>
 
 function url() {
   return Flag.OPENCODE_MODELS_URL || "https://models.dev"
diff --git a/packages/opencode/src/provider/provider.ts b/packages/opencode/src/provider/provider.ts
index d643f25373af..d826f6b35050 100644
--- a/packages/opencode/src/provider/provider.ts
+++ b/packages/opencode/src/provider/provider.ts
@@ -1,4 +1,3 @@
-import z from "zod"
 import os from "os"
 import fuzzysort from "fuzzysort"
 import { Config } from "../config"
@@ -8,7 +7,6 @@ import { Log } from "../util"
 import { Npm } from "../npm"
 import { Hash } from "@opencode-ai/shared/util/hash"
 import { Plugin } from "../plugin"
-import { NamedError } from "@opencode-ai/shared/util/error"
 import { type LanguageModelV3 } from "@ai-sdk/provider"
 import * as ModelsDev from "./models"
 import { Auth } from "../auth"
@@ -16,6 +14,7 @@ import { Env } from "../env"
 import { InstallationVersion } from "../installation/version"
 import { Flag } from "../flag/flag"
 import { zod } from "@/util/effect-zod"
+import { namedSchemaError } from "@/util/named-schema-error"
 import { iife } from "@/util/iife"
 import { Global } from "../global"
 import path from "path"
@@ -1047,7 +1046,7 @@ export function fromModelsDevProvider(provider: ModelsDev.Provider): Info {
     id: ProviderID.make(provider.id),
     source: "custom",
     name: provider.name,
-    env: provider.env ?? [],
+    env: [...(provider.env ?? [])],
     options: {},
     models,
   }
@@ -1713,18 +1712,12 @@ export function parseModel(model: string) {
   }
 }
 
-export const ModelNotFoundError = NamedError.create(
-  "ProviderModelNotFoundError",
-  z.object({
-    providerID: ProviderID.zod,
-    modelID: ModelID.zod,
-    suggestions: z.array(z.string()).optional(),
-  }),
-)
+export const ModelNotFoundError = namedSchemaError("ProviderModelNotFoundError", {
+  providerID: ProviderID,
+  modelID: ModelID,
+  suggestions: Schema.optional(Schema.Array(Schema.String)),
+})
 
-export const InitError = NamedError.create(
-  "ProviderInitError",
-  z.object({
-    providerID: ProviderID.zod,
-  }),
-)
+export const InitError = namedSchemaError("ProviderInitError", {
+  providerID: ProviderID,
+})
PATCH_EOF

git apply --whitespace=nowarn "$PATCH_FILE"
rm -f "$PATCH_FILE"

echo "Gold patch applied."
