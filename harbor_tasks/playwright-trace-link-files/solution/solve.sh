#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'traceFile?' packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/cli/program.ts b/packages/playwright-core/src/cli/program.ts
index 558ddb8170060..e47b9c41597ff 100644
--- a/packages/playwright-core/src/cli/program.ts
+++ b/packages/playwright-core/src/cli/program.ts
@@ -249,7 +249,7 @@ program
     .action(async options => {
       const { program: cliProgram } = await import('../tools/cli-client/program');
       process.argv.splice(process.argv.indexOf('cli'), 1);
-      cliProgram();
+      cliProgram().catch(logErrorAndExit);
     });

 function logErrorAndExit(e: Error) {
diff --git a/packages/playwright-core/src/tools/backend/tracing.ts b/packages/playwright-core/src/tools/backend/tracing.ts
index f042d93ff533f..075727f71246a 100644
--- a/packages/playwright-core/src/tools/backend/tracing.ts
+++ b/packages/playwright-core/src/tools/backend/tracing.ts
@@ -64,6 +64,11 @@ const tracingStop = defineTool({
     await browserContext.tracing.stop();
     // eslint-disable-next-line no-restricted-syntax
     const traceLegend = (browserContext.tracing as any)[traceLegendSymbol];
+    if (!traceLegend)
+      throw new Error('Tracing is not started');
+    // eslint-disable-next-line no-restricted-syntax
+    delete (browserContext.tracing as any)[traceLegendSymbol];
+
     response.addTextResult(`Trace recording stopped.`);
     response.addFileLink('Trace', `${traceLegend.tracesDir}/${traceLegend.name}.trace`);
     response.addFileLink('Network log', `${traceLegend.tracesDir}/${traceLegend.name}.network`);
diff --git a/packages/playwright-core/src/tools/trace/traceUtils.ts b/packages/playwright-core/src/tools/trace/traceUtils.ts
index a066d76773213..6d37f64d84a22 100644
--- a/packages/playwright-core/src/tools/trace/traceUtils.ts
+++ b/packages/playwright-core/src/tools/trace/traceUtils.ts
@@ -68,15 +68,28 @@ export async function openTrace(traceFile: string) {
     throw new Error(`Trace file not found: ${filePath}`);
   await closeTrace();
   await fs.promises.mkdir(traceDir, { recursive: true });
-  await extractTrace(filePath, traceDir);
+  if (filePath.endsWith('.zip'))
+    await extractTrace(filePath, traceDir);
+  else
+    await fs.promises.writeFile(path.join(traceDir, '.link'), filePath, 'utf-8');
 }

 export async function loadTrace(): Promise<LoadedTrace> {
   const dir = ensureTraceOpen();
-  const backend = new DirTraceLoaderBackend(dir);
+  const linkFile = path.join(dir, '.link');
+  let traceDir: string;
+  let traceFile: string | undefined;
+  if (fs.existsSync(linkFile)) {
+    const tracePath = await fs.promises.readFile(linkFile, 'utf-8');
+    traceDir = path.dirname(tracePath);
+    traceFile = path.basename(tracePath);
+  } else {
+    traceDir = dir;
+  }
+  const backend = new DirTraceLoaderBackend(traceDir);
   const loader = new TraceLoader();
-  await loader.load(backend, () => undefined);
-  const model = new TraceModel(dir, loader.contextEntries);
+  await loader.load(backend, traceFile);
+  const model = new TraceModel(traceDir, loader.contextEntries);
   return new LoadedTrace(model, loader, buildOrdinalMap(model));
 }

diff --git a/packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts b/packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts
index 5c9a1e3e22465..8547a32e142f0 100644
--- a/packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts
+++ b/packages/playwright-core/src/utils/isomorphic/trace/traceLoader.ts
@@ -38,38 +38,39 @@ export class TraceLoader {
   constructor() {
   }

-  async load(backend: TraceLoaderBackend, unzipProgress: (done: number, total: number) => void) {
+  async load(backend: TraceLoaderBackend, traceFile?: string, unzipProgress?: (done: number, total: number) => void) {
     this._backend = backend;

-    const ordinals: string[] = [];
+    const prefix = traceFile?.match(/(.+)\.trace$/)?.[1];
+    const prefixes: string[] = [];
     let hasSource = false;
     for (const entryName of await this._backend.entryNames()) {
       const match = entryName.match(/(.+)\.trace$/);
-      if (match)
-        ordinals.push(match[1] || '');
+      if (match && (!prefix || prefix  === match[1]))
+        prefixes.push(match[1] || '');
       if (entryName.includes('src@'))
         hasSource = true;
     }
-    if (!ordinals.length)
+    if (!prefixes.length)
       throw new Error('Cannot find .trace file');

     this._snapshotStorage = new SnapshotStorage();

     // 3 * ordinals progress increments below.
-    const total = ordinals.length * 3;
+    const total = prefixes.length * 3;
     let done = 0;
-    for (const ordinal of ordinals) {
+    for (const prefix of prefixes) {
       const contextEntry = createEmptyContext();
       contextEntry.hasSource = hasSource;
       const modernizer = new TraceModernizer(contextEntry, this._snapshotStorage);

-      const trace = await this._backend.readText(ordinal + '.trace') || '';
+      const trace = await this._backend.readText(prefix + '.trace') || '';
       modernizer.appendTrace(trace);
-      unzipProgress(++done, total);
+      unzipProgress?.(++done, total);

-      const network = await this._backend.readText(ordinal + '.network') || '';
+      const network = await this._backend.readText(prefix + '.network') || '';
       modernizer.appendTrace(network);
-      unzipProgress(++done, total);
+      unzipProgress?.(++done, total);

       contextEntry.actions = modernizer.actions().sort((a1, a2) => a1.startTime - a2.startTime);

@@ -87,13 +88,13 @@ export class TraceLoader {
         }
       }

-      const stacks = await this._backend.readText(ordinal + '.stacks');
+      const stacks = await this._backend.readText(prefix + '.stacks');
       if (stacks) {
         const callMetadata = parseClientSideCallMetadata(JSON.parse(stacks));
         for (const action of contextEntry.actions)
           action.stack = action.stack || callMetadata.get(action.callId);
       }
-      unzipProgress(++done, total);
+      unzipProgress?.(++done, total);

       for (const resource of contextEntry.resources) {
         if (resource.request.postData?._sha1)
diff --git a/packages/trace-viewer/src/sw/main.ts b/packages/trace-viewer/src/sw/main.ts
index 02cb68aeaff0d..15a5f23d3d8c8 100644
--- a/packages/trace-viewer/src/sw/main.ts
+++ b/packages/trace-viewer/src/sw/main.ts
@@ -111,7 +111,7 @@ async function innerLoadTrace(traceUri: string, progress: Progress): Promise<Loa
     // Allow 10% to hop from sw to page.
     const [fetchProgress, unzipProgress] = splitProgress(progress, [0.5, 0.4, 0.1]);
     const backend = isLiveTrace(traceUri) || traceUri.endsWith('traces.dir') ? new FetchTraceLoaderBackend(traceUri) : new ZipTraceLoaderBackend(traceUri, fetchProgress);
-    await traceLoader.load(backend, unzipProgress);
+    await traceLoader.load(backend, undefined, unzipProgress);
   } catch (error: any) {
     // eslint-disable-next-line no-console
     console.error(error);
diff --git a/tests/config/utils.ts b/tests/config/utils.ts
index d3d58ab54f855..85c21b8c00a44 100644
--- a/tests/config/utils.ts
+++ b/tests/config/utils.ts
@@ -170,7 +170,7 @@ export async function parseTrace(file: string): Promise<{ snapshots: SnapshotSto
   await extractTrace(file, dir);
   const backend = new DirTraceLoaderBackend(dir);
   const loader = new TraceLoader();
-  await loader.load(backend, () => {});
+  await loader.load(backend);
   return { model: new TraceModel(dir, loader.contextEntries), snapshots: loader.storage() };
 }

PATCH

echo "Patch applied successfully."
