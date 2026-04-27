#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: skip if already applied (distinctive line from the patch)
if grep -q 'class OutputFormatText extends Schema.Class<OutputFormatText>' \
        packages/opencode/src/session/message-v2.ts 2>/dev/null; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/specs/effect/schema.md b/packages/opencode/specs/effect/schema.md
index 2fcbfc12bef6..6deea49655e5 100644
--- a/packages/opencode/specs/effect/schema.md
+++ b/packages/opencode/specs/effect/schema.md
@@ -186,6 +186,80 @@ schema module with a clear domain.
 Major cluster. Message + event types flow through the SSE API and every SDK
 output, so byte-identical SDK surface is critical.

+Suggested order for this cluster, starting from the leaves that `session.ts`
+and the SSE/event surface depend on:
+
+1. `src/session/schema.ts` ✅ already migrated
+2. `src/provider/schema.ts` if `message-v2.ts` still relies on zod-first IDs
+3. `src/lsp/*` schema leaves needed by `LSP.Range`
+4. `src/snapshot/*` leaves used by `Snapshot.FileDiff`
+5. `src/session/message-v2.ts`
+6. `src/session/message.ts`
+7. `src/session/prompt.ts`
+8. `src/session/revert.ts`
+9. `src/session/summary.ts`
+10. `src/session/status.ts`
+11. `src/session/todo.ts`
+12. `src/session/session.ts`
+13. `src/session/compaction.ts`
+
+Dependency sketch:
+
+```text
+session.ts
+|- project/schema.ts
+|- control-plane/schema.ts
+|- permission/schema.ts
+|- snapshot/*
+|- message-v2.ts
+|  |- provider/schema.ts
+|  |- lsp/*
+|  |- snapshot/*
+|  |- sync/index.ts
+|  `- bus/bus-event.ts
+|- sync/index.ts
+|- bus/bus-event.ts
+`- util/update-schema.ts
+```
+
+Working rule for this cluster:
+
+- migrate reusable leaf schemas and nested payload objects first
+- migrate aggregate DTOs like `Session.Info` after their nested pieces exist as
+  named Schema values
+- leave zod-only event/update helpers in place temporarily when converting
+  them would force unrelated churn across sync/bus boundaries
+
+`message-v2.ts` first-pass outline:
+
+1. Schema-backed imports already available
+   - `SessionID`, `MessageID`, `PartID`
+   - `ProviderID`, `ModelID`
+2. Local leaf objects to extract and migrate first
+   - output format payloads
+   - common part bases like `PartBase`
+   - timestamp/range helper objects like `time.start/end`
+   - file/source helper objects
+   - token/cost/model helper objects
+3. Part variants built from those leaves
+   - `SnapshotPart`, `PatchPart`, `TextPart`, `ReasoningPart`
+   - `FilePart`, `AgentPart`, `CompactionPart`, `SubtaskPart`
+   - retry/step/tool related parts
+4. Higher-level unions and DTOs
+   - `FilePartSource`
+   - part unions
+   - message unions and assistant/user payloads
+5. Errors and event payloads last
+   - `NamedError.create(...)` shapes can stay temporarily if converting them to
+     `Schema.TaggedErrorClass` would force unrelated churn
+   - `SyncEvent.define(...)` and `BusEvent.define(...)` payloads can keep using
+     derived `.zod` until the sync/bus layers are migrated
+
+Possible later tightening after the Schema-first migration is stable:
+
+- promote repeated opaque strings and timestamp numbers into branded/newtype
+  leaf schemas where that adds domain value without changing the wire format
+
 - [ ] `src/session/compaction.ts`
 - [ ] `src/session/message-v2.ts`
 - [ ] `src/session/message.ts`
diff --git a/packages/opencode/src/session/message-v2.ts b/packages/opencode/src/session/message-v2.ts
index 20528763b8b1..640be2ab8268 100644
--- a/packages/opencode/src/session/message-v2.ts
+++ b/packages/opencode/src/session/message-v2.ts
@@ -15,7 +15,8 @@ import { isMedia } from "@/util/media"
 import type { SystemError } from "bun"
 import type { Provider } from "@/provider"
 import { ModelID, ProviderID } from "@/provider/schema"
-import { Effect } from "effect"
+import { Effect, Schema } from "effect"
+import { zod } from "@/util/effect-zod"
 import { EffectLogger } from "@/effect"

 /** Error shape thrown by Bun's fetch() when gzip/br decompression fails mid-stream */
@@ -61,28 +62,28 @@ export const ContextOverflowError = NamedError.create(
   z.object({ message: z.string(), responseBody: z.string().optional() }),
 )

-export const OutputFormatText = z
-  .object({
-    type: z.literal("text"),
-  })
-  .meta({
-    ref: "OutputFormatText",
-  })
+export class OutputFormatText extends Schema.Class<OutputFormatText>("OutputFormatText")({
+  type: Schema.Literal("text"),
+}) {
+  static readonly zod = zod(this)
+}

-export const OutputFormatJsonSchema = z
-  .object({
-    type: z.literal("json_schema"),
-    schema: z.record(z.string(), z.any()).meta({ ref: "JSONSchema" }),
-    retryCount: z.number().int().min(0).default(2),
-  })
-  .meta({
-    ref: "OutputFormatJsonSchema",
-  })
+export class OutputFormatJsonSchema extends Schema.Class<OutputFormatJsonSchema>("OutputFormatJsonSchema")({
+  type: Schema.Literal("json_schema"),
+  schema: Schema.Record(Schema.String, Schema.Any).annotate({ identifier: "JSONSchema" }),
+  retryCount: Schema.Number.check(Schema.isInt())
+    .check(Schema.isGreaterThanOrEqualTo(0))
+    .pipe(Schema.optional, Schema.withDecodingDefault(Effect.succeed(2))),
+}) {
+  static readonly zod = zod(this)
+}

-export const Format = z.discriminatedUnion("type", [OutputFormatText, OutputFormatJsonSchema]).meta({
-  ref: "OutputFormat",
+const _Format = Schema.Union([OutputFormatText, OutputFormatJsonSchema]).annotate({
+  discriminator: "type",
+  identifier: "OutputFormat",
 })
-export type OutputFormat = z.infer<typeof Format>
+export const Format = Object.assign(_Format, { zod: zod(_Format) })
+export type OutputFormat = Schema.Schema.Type<typeof _Format>

 const PartBase = z.object({
   id: PartID.zod,
@@ -360,7 +361,7 @@ export const User = Base.extend({
   time: z.object({
     created: z.number(),
   }),
-  format: Format.optional(),
+  format: Format.zod.optional(),
   summary: z
     .object({
       title: z.string().optional(),
diff --git a/packages/opencode/src/session/prompt.ts b/packages/opencode/src/session/prompt.ts
index 431189d19cc0..6dcec0459259 100644
--- a/packages/opencode/src/session/prompt.ts
+++ b/packages/opencode/src/session/prompt.ts
@@ -1716,7 +1716,7 @@ export const PromptInput = z.object({
     .record(z.string(), z.boolean())
     .optional()
     .describe("@deprecated tools and permissions have been merged, you can set permissions on the session itself now"),
-  format: MessageV2.Format.optional(),
+  format: MessageV2.Format.zod.optional(),
   system: z.string().optional(),
   variant: z.string().optional(),
   parts: z.array(
diff --git a/packages/opencode/test/session/structured-output.test.ts b/packages/opencode/test/session/structured-output.test.ts
index 2debfb76d57d..a91446bf4288 100644
--- a/packages/opencode/test/session/structured-output.test.ts
+++ b/packages/opencode/test/session/structured-output.test.ts
@@ -5,7 +5,7 @@ import { SessionID, MessageID } from "../../src/session/schema"

 describe("structured-output.OutputFormat", () => {
   test("parses text format", () => {
-    const result = MessageV2.Format.safeParse({ type: "text" })
+    const result = MessageV2.Format.zod.safeParse({ type: "text" })
     expect(result.success).toBe(true)
     if (result.success) {
       expect(result.data.type).toBe("text")
@@ -13,7 +13,7 @@ describe("structured-output.OutputFormat", () => {
   })

   test("parses json_schema format with defaults", () => {
-    const result = MessageV2.Format.safeParse({
+    const result = MessageV2.Format.zod.safeParse({
       type: "json_schema",
       schema: { type: "object", properties: { name: { type: "string" } } },
     })
@@ -27,7 +27,7 @@ describe("structured-output.OutputFormat", () => {
   })

   test("parses json_schema format with custom retryCount", () => {
-    const result = MessageV2.Format.safeParse({
+    const result = MessageV2.Format.zod.safeParse({
       type: "json_schema",
       schema: { type: "object" },
       retryCount: 5,
@@ -39,17 +39,17 @@ describe("structured-output.OutputFormat", () => {
   })

   test("rejects invalid type", () => {
-    const result = MessageV2.Format.safeParse({ type: "invalid" })
+    const result = MessageV2.Format.zod.safeParse({ type: "invalid" })
     expect(result.success).toBe(false)
   })

   test("rejects json_schema without schema", () => {
-    const result = MessageV2.Format.safeParse({ type: "json_schema" })
+    const result = MessageV2.Format.zod.safeParse({ type: "json_schema" })
     expect(result.success).toBe(false)
   })

   test("rejects negative retryCount", () => {
-    const result = MessageV2.Format.safeParse({
+    const result = MessageV2.Format.zod.safeParse({
       type: "json_schema",
       schema: { type: "object" },
       retryCount: -1,
PATCH

echo "Gold patch applied."
