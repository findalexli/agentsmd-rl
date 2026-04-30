#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'export async function closeTrace' packages/playwright-core/src/tools/trace/traceUtils.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/trace/SKILL.md b/packages/playwright-core/src/tools/trace/SKILL.md
index 8e4dd44332a5c..6cf0af85ab8a2 100644
--- a/packages/playwright-core/src/tools/trace/SKILL.md
+++ b/packages/playwright-core/src/tools/trace/SKILL.md
@@ -15,6 +15,7 @@ Inspect `.zip` trace files produced by Playwright tests without opening a browse
 3. Use `trace action <action-id>` to drill into a specific action — see parameters, logs, source location, and available snapshots.
 4. Use `trace requests`, `trace console`, or `trace errors` for cross-cutting views.
 5. Use `trace snapshot <action-id>` to get the DOM snapshot, or run a browser command against it.
+6. Use `trace close` to remove the extracted trace data when done.

 All commands after `open` operate on the currently opened trace — no need to pass the trace file again. Opening a new trace replaces the previous one.

@@ -27,6 +28,13 @@ All commands after `open` operate on the currently opened trace — no need to p
 npx playwright trace open <trace.zip>
 ```

+### Close a trace
+
+```bash
+# Remove extracted trace data
+npx playwright trace close
+```
+
 ### Actions

 ```bash
diff --git a/packages/playwright-core/src/tools/trace/traceCli.ts b/packages/playwright-core/src/tools/trace/traceCli.ts
index 79cc46f6a0dcf..5bb76135c2fc0 100644
--- a/packages/playwright-core/src/tools/trace/traceCli.ts
+++ b/packages/playwright-core/src/tools/trace/traceCli.ts
@@ -29,6 +29,14 @@ export function addTraceCommands(program: Command, logErrorAndExit: (e: Error) =
         traceOpen(trace).catch(logErrorAndExit);
       });

+  traceCommand
+      .command('close')
+      .description('remove extracted trace data')
+      .action(async () => {
+        const { closeTrace } = await import('./traceUtils');
+        closeTrace().catch(logErrorAndExit);
+      });
+
   traceCommand
       .command('actions')
       .description('list actions in the trace')
diff --git a/packages/playwright-core/src/tools/trace/traceUtils.ts b/packages/playwright-core/src/tools/trace/traceUtils.ts
index 9dae3b2e4f8c8..a066d76773213 100644
--- a/packages/playwright-core/src/tools/trace/traceUtils.ts
+++ b/packages/playwright-core/src/tools/trace/traceUtils.ts
@@ -57,12 +57,16 @@ function ensureTraceOpen(): string {
   return traceDir;
 }

+export async function closeTrace() {
+  if (fs.existsSync(traceDir))
+    await fs.promises.rm(traceDir, { recursive: true });
+}
+
 export async function openTrace(traceFile: string) {
   const filePath = path.resolve(traceFile);
   if (!fs.existsSync(filePath))
     throw new Error(`Trace file not found: ${filePath}`);
-  if (fs.existsSync(traceDir))
-    await fs.promises.rm(traceDir, { recursive: true });
+  await closeTrace();
   await fs.promises.mkdir(traceDir, { recursive: true });
   await extractTrace(filePath, traceDir);
 }

PATCH

echo "Patch applied successfully."
