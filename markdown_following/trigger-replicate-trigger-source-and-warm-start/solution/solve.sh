#!/bin/bash
# Gold solution: applies the merged patch from PR #3274 inline.
set -euo pipefail

cd /workspace/trigger.dev

# Idempotency: if the new ClickHouse migration file already exists with
# the new column DDL, the patch has already been applied — exit cleanly.
if grep -q "ADD COLUMN trigger_source LowCardinality" \
     internal-packages/clickhouse/schema/028_add_trigger_source_and_warm_start_to_task_runs_v2.sql 2>/dev/null; then
  echo "[solve.sh] Patch already applied; nothing to do."
  exit 0
fi

# Inline gold patch (do NOT fetch externally — the oracle must be self-contained).
cat > /tmp/pr3274.patch <<'PATCH_EOF_SENTINEL'
diff --git a/apps/webapp/app/services/runsReplicationService.server.ts b/apps/webapp/app/services/runsReplicationService.server.ts
index 56e2be62d41..7930c05481f 100644
--- a/apps/webapp/app/services/runsReplicationService.server.ts
+++ b/apps/webapp/app/services/runsReplicationService.server.ts
@@ -22,6 +22,7 @@ import { Logger, type LogLevel } from "@trigger.dev/core/logger";
 import { tryCatch } from "@trigger.dev/core/utils";
 import { parsePacketAsJson } from "@trigger.dev/core/v3/utils/ioSerialization";
 import { unsafeExtractIdempotencyKeyScope, unsafeExtractIdempotencyKeyUser } from "@trigger.dev/core/v3/serverOnly";
+import { RunAnnotations } from "@trigger.dev/core/v3";
 import { type TaskRun } from "@trigger.dev/database";
 import { nanoid } from "nanoid";
 import EventEmitter from "node:events";
@@ -866,6 +867,8 @@ export class RunsReplicationService {
       ? calculateErrorFingerprint(run.error)
       : '';
 
+    const annotations = this.#parseAnnotations(run.annotations);
+
     // Return array matching TASK_RUN_COLUMNS order
     return [
       run.runtimeEnvironmentId, // environment_id
@@ -916,9 +919,16 @@ export class RunsReplicationService {
       run.bulkActionGroupIds ?? [], // bulk_action_group_ids
       run.masterQueue ?? "", // worker_queue
       run.maxDurationInSeconds ?? null, // max_duration_in_seconds
+      annotations?.triggerSource ?? "", // trigger_source
+      annotations?.rootTriggerSource ?? "", // root_trigger_source
+      run.isWarmStart ?? null, // is_warm_start
     ];
   }
 
+  #parseAnnotations(annotations: unknown) {
+    return RunAnnotations.safeParse(annotations).data;
+  }
+
   async #preparePayloadInsert(run: TaskRun, _version: bigint): Promise<PayloadInsertArray> {
     const payload = await this.#prepareJson(run.payload, run.payloadType);
 
diff --git a/apps/webapp/test/runsReplicationService.part1.test.ts b/apps/webapp/test/runsReplicationService.part1.test.ts
index 87ebd0cde2d..715d4583dc2 100644
--- a/apps/webapp/test/runsReplicationService.part1.test.ts
+++ b/apps/webapp/test/runsReplicationService.part1.test.ts
@@ -86,6 +86,12 @@ describe("RunsReplicationService (part 1/2)", () => {
           organizationId: organization.id,
           environmentType: "DEVELOPMENT",
           engine: "V2",
+          annotations: {
+            triggerSource: "api",
+            triggerAction: "trigger",
+            rootTriggerSource: "dashboard",
+          },
+          isWarmStart: true,
         },
       });
 
@@ -111,6 +117,9 @@ describe("RunsReplicationService (part 1/2)", () => {
           organization_id: organization.id,
           environment_type: "DEVELOPMENT",
           engine: "V2",
+          trigger_source: "api",
+          root_trigger_source: "dashboard",
+          is_warm_start: 1,
         })
       );
 
diff --git a/internal-packages/clickhouse/schema/028_add_trigger_source_and_warm_start_to_task_runs_v2.sql b/internal-packages/clickhouse/schema/028_add_trigger_source_and_warm_start_to_task_runs_v2.sql
new file mode 100644
index 00000000000..9381df8ddd5
--- /dev/null
+++ b/internal-packages/clickhouse/schema/028_add_trigger_source_and_warm_start_to_task_runs_v2.sql
@@ -0,0 +1,19 @@
+-- +goose Up
+ALTER TABLE trigger_dev.task_runs_v2
+  ADD COLUMN trigger_source LowCardinality(String) DEFAULT '';
+
+ALTER TABLE trigger_dev.task_runs_v2
+  ADD COLUMN root_trigger_source LowCardinality(String) DEFAULT '';
+
+ALTER TABLE trigger_dev.task_runs_v2
+  ADD COLUMN is_warm_start Nullable(UInt8) DEFAULT NULL;
+
+-- +goose Down
+ALTER TABLE trigger_dev.task_runs_v2
+  DROP COLUMN trigger_source;
+
+ALTER TABLE trigger_dev.task_runs_v2
+  DROP COLUMN root_trigger_source;
+
+ALTER TABLE trigger_dev.task_runs_v2
+  DROP COLUMN is_warm_start;
diff --git a/internal-packages/clickhouse/src/taskRuns.test.ts b/internal-packages/clickhouse/src/taskRuns.test.ts
index 51a2a8d996c..8bd403f14f0 100644
--- a/internal-packages/clickhouse/src/taskRuns.test.ts
+++ b/internal-packages/clickhouse/src/taskRuns.test.ts
@@ -82,6 +82,9 @@ describe("Task Runs V2", () => {
       ["bulk_action_group_id_1234", "bulk_action_group_id_1235"], // bulk_action_group_ids
       "", // worker_queue
       null, // max_duration_in_seconds
+      "", // trigger_source
+      "", // root_trigger_source
+      null, // is_warm_start
     ];
 
     const [insertError, insertResult] = await insert([taskRunData]);
@@ -210,6 +213,9 @@ describe("Task Runs V2", () => {
       [], // bulk_action_group_ids
       "", // worker_queue
       null, // max_duration_in_seconds
+      "", // trigger_source
+      "", // root_trigger_source
+      null, // is_warm_start
     ];
 
     const run2: TaskRunInsertArray = [
@@ -261,6 +267,9 @@ describe("Task Runs V2", () => {
       [], // bulk_action_group_ids
       "", // worker_queue
       null, // max_duration_in_seconds
+      "", // trigger_source
+      "", // root_trigger_source
+      null, // is_warm_start
     ];
 
     const [insertError, insertResult] = await insert([run1, run2]);
@@ -359,6 +368,9 @@ describe("Task Runs V2", () => {
         [], // bulk_action_group_ids
         "", // worker_queue
         null, // max_duration_in_seconds
+        "", // trigger_source
+        "", // root_trigger_source
+        null, // is_warm_start
       ];
 
       const [insertError, insertResult] = await insert([taskRun]);
diff --git a/internal-packages/clickhouse/src/taskRuns.ts b/internal-packages/clickhouse/src/taskRuns.ts
index 4162691ed7a..6a9f66d7844 100644
--- a/internal-packages/clickhouse/src/taskRuns.ts
+++ b/internal-packages/clickhouse/src/taskRuns.ts
@@ -49,6 +49,9 @@ export const TaskRunV2 = z.object({
   bulk_action_group_ids: z.array(z.string()).default([]),
   worker_queue: z.string().default(""),
   max_duration_in_seconds: z.number().int().nullish(),
+  trigger_source: z.string().default(""),
+  root_trigger_source: z.string().default(""),
+  is_warm_start: z.boolean().nullish(),
   _version: z.string(),
   _is_deleted: z.number().int().default(0),
 });
@@ -105,6 +108,9 @@ export const TASK_RUN_COLUMNS = [
   "bulk_action_group_ids",
   "worker_queue",
   "max_duration_in_seconds",
+  "trigger_source",
+  "root_trigger_source",
+  "is_warm_start",
 ] as const;
 
 export type TaskRunColumnName = (typeof TASK_RUN_COLUMNS)[number];
@@ -168,6 +174,9 @@ export type TaskRunFieldTypes = {
   bulk_action_group_ids: string[];
   worker_queue: string;
   max_duration_in_seconds: number | null;
+  trigger_source: string;
+  root_trigger_source: string;
+  is_warm_start: boolean | null;
 };
 
 /**
@@ -302,6 +311,9 @@ export type TaskRunInsertArray = [
   bulk_action_group_ids: string[],
   worker_queue: string,
   max_duration_in_seconds: number | null,
+  trigger_source: string,
+  root_trigger_source: string,
+  is_warm_start: boolean | null,
 ];
 
 /**
diff --git a/internal-packages/database/prisma/migrations/20260325165730_add_is_warm_start_to_task_run/migration.sql b/internal-packages/database/prisma/migrations/20260325165730_add_is_warm_start_to_task_run/migration.sql
new file mode 100644
index 00000000000..29274427d3c
--- /dev/null
+++ b/internal-packages/database/prisma/migrations/20260325165730_add_is_warm_start_to_task_run/migration.sql
@@ -0,0 +1,2 @@
+-- AlterTable
+ALTER TABLE "public"."TaskRun" ADD COLUMN "isWarmStart" BOOLEAN;
diff --git a/internal-packages/database/prisma/schema.prisma b/internal-packages/database/prisma/schema.prisma
index bf3c946a985..ceb10f7549b 100644
--- a/internal-packages/database/prisma/schema.prisma
+++ b/internal-packages/database/prisma/schema.prisma
@@ -537,13 +537,13 @@ model BackgroundWorkerFile {
 }
 
 model Prompt {
-  id         String @id @default(cuid())
-  friendlyId String @unique @map("friendly_id")
+  id          String  @id @default(cuid())
+  friendlyId  String  @unique @map("friendly_id")
   slug        String
   description String?
   type        String  @default("text") // "text" | "chat"
 
-  organization   Organization       @relation(fields: [organizationId], references: [id], onDelete: Cascade, onUpdate: Cascade)
+  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade, onUpdate: Cascade)
   organizationId String
 
   project   Project @relation(fields: [projectId], references: [id], onDelete: Cascade, onUpdate: Cascade)
@@ -558,7 +558,7 @@ model Prompt {
   defaultModel   String?
   defaultConfig  Json?
 
-  tags       String[] @default([])
+  tags       String[]  @default([])
   archivedAt DateTime?
 
   createdAt DateTime @default(now())
@@ -840,6 +840,9 @@ model TaskRun {
   /// Structured annotations: triggerSource, triggerAction, rootTriggerSource, rootScheduleId
   annotations Json?
 
+  /// Whether the latest attempt was a warm start. Null until first attempt starts.
+  isWarmStart Boolean?
+
   /// Run output
   output     String?
   outputType String  @default("application/json")
@@ -857,7 +860,6 @@ model TaskRun {
   /// Store the stream keys that are being used by the run
   realtimeStreams        String[] @default([])
 
-
   @@unique([oneTimeUseToken])
   @@unique([runtimeEnvironmentId, taskIdentifier, idempotencyKey])
   // Finding child runs
diff --git a/internal-packages/run-engine/src/engine/systems/runAttemptSystem.ts b/internal-packages/run-engine/src/engine/systems/runAttemptSystem.ts
index 067d00a14e0..8e95519241c 100644
--- a/internal-packages/run-engine/src/engine/systems/runAttemptSystem.ts
+++ b/internal-packages/run-engine/src/engine/systems/runAttemptSystem.ts
@@ -402,6 +402,7 @@ export class RunAttemptSystem {
                   status: "EXECUTING",
                   attemptNumber: nextAttemptNumber,
                   executedAt: taskRun.attemptNumber === null ? new Date() : undefined,
+                  isWarmStart: isWarmStart ?? false,
                 },
                 select: {
                   id: true,
PATCH_EOF_SENTINEL

git apply --whitespace=nowarn /tmp/pr3274.patch
echo "[solve.sh] Patch applied successfully."
