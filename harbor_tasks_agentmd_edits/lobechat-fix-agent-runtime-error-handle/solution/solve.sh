#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'partialToSnapshot' packages/agent-tracing/src/store/file-store.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/agent-tracing/SKILL.md b/.agents/skills/agent-tracing/SKILL.md
index 49867b3fe20..ea0b3ed4b18 100644
--- a/.agents/skills/agent-tracing/SKILL.md
+++ b/.agents/skills/agent-tracing/SKILL.md
@@ -96,10 +96,10 @@ agent-tracing inspect <traceId> -s 0 -j
 # List in-progress partial snapshots
 agent-tracing partial list

-# Inspect a partial snapshot (defaults to latest)
-agent-tracing partial inspect
-agent-tracing partial inspect <operationId>
-agent-tracing partial inspect -j
+# Inspect a partial (use `inspect` directly — all flags work with partial IDs)
+agent-tracing inspect <partialOperationId>
+agent-tracing inspect <partialOperationId> -T
+agent-tracing inspect <partialOperationId> -p

 # Clean up stale partial snapshots
 agent-tracing partial clean
diff --git a/packages/agent-tracing/src/cli/partial.ts b/packages/agent-tracing/src/cli/partial.ts
index a91e1a9fde6..449763785d2 100644
--- a/packages/agent-tracing/src/cli/partial.ts
+++ b/packages/agent-tracing/src/cli/partial.ts
@@ -1,11 +1,9 @@
 import type { Command } from 'commander';

 import { FileSnapshotStore } from '../store/file-store';
-import type { ExecutionSnapshot } from '../types';
-import { renderSnapshot } from '../viewer';

 export function registerPartialCommand(program: Command) {
-  const partial = program.command('partial').description('Inspect in-progress (partial) snapshots');
+  const partial = program.command('partial').description('Manage in-progress (partial) snapshots');

   partial
     .command('list')
@@ -36,54 +34,10 @@ export function registerPartialCommand(program: Command) {
           console.log(`  ${file}`);
         }
       }
-    });
-
-  partial
-    .command('inspect')
-    .alias('view')
-    .description('Inspect a partial snapshot')
-    .argument('[id]', 'Partial operation ID or filename (defaults to latest)')
-    .option('-j, --json', 'Output as JSON')
-    .action(async (id: string | undefined, opts: { json?: boolean }) => {
-      const store = new FileSnapshotStore();
-      const files = await store.listPartials();
-
-      if (files.length === 0) {
-        console.error('No partial snapshots found.');
-        process.exit(1);
-      }
-
-      const data = id ? await store.getPartial(id) : await store.getPartial(files[0]);
-
-      if (!data) {
-        console.error(id ? `Partial not found: ${id}` : 'No partial snapshots found.');
-        process.exit(1);
-      }
-
-      if (opts.json) {
-        console.log(JSON.stringify(data, null, 2));
-        return;
-      }
-
-      // Render as a snapshot (fill in defaults for missing fields)
-      const snapshot: ExecutionSnapshot = {
-        completedAt: undefined,
-        completionReason: undefined,
-        error: undefined,
-        model: data.model,
-        operationId: data.operationId ?? '?',
-        provider: data.provider,
-        startedAt: data.startedAt ?? Date.now(),
-        steps: data.steps ?? [],
-        totalCost: data.totalCost ?? 0,
-        totalSteps: data.steps?.length ?? 0,
-        totalTokens: data.totalTokens ?? 0,
-        traceId: data.traceId ?? '?',
-        ...data,
-      };

-      console.log('[PARTIAL - in progress]\n');
-      console.log(renderSnapshot(snapshot));
+      console.log(
+        `\nUse ${`"agent-tracing inspect <id>"`.toString()} to inspect a partial with full flags.`,
+      );
     });

   partial
diff --git a/packages/agent-tracing/src/store/file-store.ts b/packages/agent-tracing/src/store/file-store.ts
index 7b498dcb4a2..11757208053 100644
--- a/packages/agent-tracing/src/store/file-store.ts
+++ b/packages/agent-tracing/src/store/file-store.ts
@@ -39,12 +39,19 @@ export class FileSnapshotStore implements ISnapshotStore {
   async get(traceId: string): Promise<ExecutionSnapshot | null> {
     if (traceId === 'latest') return this.getLatest();

+    // Search completed snapshots first
     const files = await this.listFiles();
     const match = files.find((f) => f.includes(traceId.slice(0, 12)));
-    if (!match) return null;
+    if (match) {
+      const content = await fs.readFile(path.join(this.dir, match), 'utf8');
+      return JSON.parse(content) as ExecutionSnapshot;
+    }
+
+    // Fallback to partials
+    const partial = await this.getPartial(traceId);
+    if (partial) return partialToSnapshot(partial);

-    const content = await fs.readFile(path.join(this.dir, match), 'utf8');
-    return JSON.parse(content) as ExecutionSnapshot;
+    return null;
   }

   async list(options?: { limit?: number }): Promise<SnapshotSummary[]> {
@@ -161,6 +168,24 @@ export class FileSnapshotStore implements ISnapshotStore {
   }
 }

+function partialToSnapshot(partial: Partial<ExecutionSnapshot>): ExecutionSnapshot {
+  return {
+    completedAt: undefined,
+    completionReason: undefined,
+    error: undefined,
+    model: partial.model,
+    operationId: partial.operationId ?? '?',
+    provider: partial.provider,
+    startedAt: partial.startedAt ?? Date.now(),
+    steps: partial.steps ?? [],
+    totalCost: partial.totalCost ?? 0,
+    totalSteps: partial.steps?.length ?? 0,
+    totalTokens: partial.totalTokens ?? 0,
+    traceId: partial.traceId ?? '?',
+    ...partial,
+  } as ExecutionSnapshot;
+}
+
 function toSummary(snapshot: ExecutionSnapshot): SnapshotSummary {
   return {
     completionReason: snapshot.completionReason,
diff --git a/src/server/services/agentRuntime/AgentRuntimeService.ts b/src/server/services/agentRuntime/AgentRuntimeService.ts
index 74a78d8bb94..03abbba8e9f 100644
--- a/src/server/services/agentRuntime/AgentRuntimeService.ts
+++ b/src/server/services/agentRuntime/AgentRuntimeService.ts
@@ -907,30 +907,56 @@ export class AgentRuntimeService {
     } catch (error) {
       log('Step %d failed for operation %s: %O', stepIndex, operationId, error);

-      // Publish error event
-      await this.streamManager.publishStreamEvent(operationId, {
-        data: {
-          error: (error as Error).message,
-          phase: 'step_execution',
+      // Build error state — try loading current state from coordinator, but if that
+      // also fails (e.g. Redis ECONNRESET), fall back to a minimal error state so
+      // that completion callbacks and webhooks can still fire.
+      let finalStateWithError: any;
+      try {
+        await this.streamManager.publishStreamEvent(operationId, {
+          data: {
+            error: (error as Error).message,
+            phase: 'step_execution',
+            stepIndex,
+          },
           stepIndex,
-        },
-        stepIndex,
-        type: 'error',
-      });
+          type: 'error',
+        });
+      } catch (publishError) {
+        log(
+          '[%s] Failed to publish error event (infra may be down): %O',
+          operationId,
+          publishError,
+        );
+      }

-      // Build and save error state so it's persisted for later retrieval
-      const errorState = await this.coordinator.loadAgentState(operationId);
-      const finalStateWithError = {
-        ...errorState!,
-        error: formatErrorForState(error),
-        status: 'error' as const,
-      };
+      try {
+        const errorState = await this.coordinator.loadAgentState(operationId);
+        finalStateWithError = {
+          ...errorState!,
+          error: formatErrorForState(error),
+          status: 'error' as const,
+        };
+      } catch (loadError) {
+        log('[%s] Failed to load error state (infra may be down): %O', operationId, loadError);
+        // Fallback: construct a minimal error state so callbacks still receive useful info
+        finalStateWithError = {
+          error: formatErrorForState(error),
+          status: 'error' as const,
+        };
+      }

-      // Save the error state to coordinator so getOperationStatus can retrieve it
-      await this.coordinator.saveAgentState(operationId, finalStateWithError);
+      try {
+        await this.coordinator.saveAgentState(operationId, finalStateWithError);
+      } catch (saveError) {
+        log('[%s] Failed to save error state (infra may be down): %O', operationId, saveError);
+      }

       // Trigger completion webhook on error (fire-and-forget)
-      await this.triggerCompletionWebhook(finalStateWithError, operationId, 'error');
+      try {
+        await this.triggerCompletionWebhook(finalStateWithError, operationId, 'error');
+      } catch (webhookError) {
+        log('[%s] Failed to trigger completion webhook: %O', operationId, webhookError);
+      }

       // Also call onComplete callback when execution fails
       if (callbacks?.onComplete) {

PATCH

echo "Patch applied successfully."
