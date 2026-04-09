#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'turboFlag: bundler === Bundler.Turbopack' packages/next/src/build/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/build/index.ts b/packages/next/src/build/index.ts
index be61dccb76dd5f..c425b8cfd2aff8 100644
--- a/packages/next/src/build/index.ts
+++ b/packages/next/src/build/index.ts
@@ -874,7 +874,8 @@ async function writeFullyStaticExport(
   enabledDirectories: NextEnabledDirectories,
   configOutDir: string,
   nextBuildSpan: Span,
-  appDirOnly: boolean
+  appDirOnly: boolean,
+  bundler: Bundler
   // TODO: Reusing the worker seems to break finding if it's `.html` or a JS page.
   // Because writeFullyStaticExport is called after `exportApp` has been called before
   // worker: StaticWorker | undefined
@@ -892,6 +893,7 @@ async function writeFullyStaticExport(
       outdir: path.join(dir, configOutDir),
       numWorkers: getNumberOfWorkers(config),
       appDirOnly,
+      bundler,
     },
     nextBuildSpan
     // worker
@@ -1166,7 +1168,7 @@ export default async function build(
           isSrcDir,
           hasNowJson: !!(await findUp('now.json', { cwd: dir })),
           isCustomServer: null,
-          turboFlag: false,
+          turboFlag: bundler === Bundler.Turbopack,
           pagesDir: !!pagesDir,
           appDir: !!appDir,
         })
@@ -2997,6 +2999,7 @@ export default async function build(
               statusMessage: `Generating static pages using ${numberOfWorkers} worker${numberOfWorkers > 1 ? 's' : ''}`,
               numWorkers: numberOfWorkers,
               appDirOnly,
+              bundler,
             },
             nextBuildSpan,
             staticWorker
@@ -4123,7 +4126,8 @@ export default async function build(
               enabledDirectories,
               configOutDir,
               nextBuildSpan,
-              appDirOnly
+              appDirOnly,
+              bundler
               // staticWorker
             )
           })
diff --git a/packages/next/src/export/index.ts b/packages/next/src/export/index.ts
index a12f8f7044e62e..b7df13c1322fb3 100644
--- a/packages/next/src/export/index.ts
+++ b/packages/next/src/export/index.ts
@@ -73,6 +73,7 @@ import { getParams } from './helpers/get-params'
 import { isDynamicRoute } from '../shared/lib/router/utils/is-dynamic'
 import { normalizeAppPath } from '../shared/lib/router/utils/app-paths'
 import type { Params } from '../server/request/params'
+import { Bundler } from '../lib/bundler'

 export class ExportError extends Error {
   code = 'NEXT_EXPORT_ERROR'
@@ -220,7 +221,7 @@ async function exportAppImpl(
         isSrcDir: null,
         hasNowJson: !!(await findUp('now.json', { cwd: dir })),
         isCustomServer: null,
-        turboFlag: false,
+        turboFlag: options.bundler === Bundler.Turbopack,
         pagesDir: null,
         appDir: null,
       })
diff --git a/packages/next/src/export/types.ts b/packages/next/src/export/types.ts
index cd8419ac7fc2eb..0098353ad11b25 100644
--- a/packages/next/src/export/types.ts
+++ b/packages/next/src/export/types.ts
@@ -16,6 +16,7 @@ import type { FetchMetrics } from '../server/base-http'
 import type { RouteMetadata } from './routes/types'
 import type { RenderResumeDataCache } from '../server/resume-data-cache/resume-data-cache'
 import type { StaticWorker } from '../build'
+import type { Bundler } from '../lib/bundler'

 export type ExportPathEntry = ExportPathMap[keyof ExportPathMap] & {
   path: string
@@ -113,6 +114,7 @@ export interface ExportAppOptions {
   hasOutdirFromCli?: boolean
   numWorkers: number
   appDirOnly: boolean
+  bundler: Bundler
 }

 export type ExportPageMetadata = {

PATCH

echo "Patch applied successfully."
