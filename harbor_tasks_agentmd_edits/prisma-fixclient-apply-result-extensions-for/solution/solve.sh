#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q 'resolveResultExtensionContext' packages/client/src/runtime/getPrismaClient.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch (code fix + AGENTS.md update)
git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index f881bbc8fcb4..509d36d2434b 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -36,6 +36,8 @@
   - `QueryInterpreter` class in `packages/client-engine-runtime/src/interpreter/query-interpreter.ts` executes query plans against `SqlQueryable` (driver adapter interface).
   - Query flow: `PrismaClient` → `ClientEngine.request()` → query compiler → `executor.execute()` → `QueryInterpreter.run()` → driver adapter.
   - `ExecutePlanParams` interface in `packages/client/src/runtime/core/engines/client/Executor.ts` defines what's passed through the execution chain.
+  - Fluent API `dataPath` is built in `packages/client/src/runtime/core/model/applyFluent.ts` by appending `['select', <relationName>]` on each hop; runtime unpacking in `packages/client/src/runtime/RequestHandler.ts` currently strips `'select'`/`'include'` segments before `deepGet`.
+  - In extension context resolution, `dataPath` should be interpreted as selector/field pairs (`select|include`, relation field). Do not strip by raw string value or relation fields literally named `select`/`include` get dropped.

 - **Adding PrismaClient constructor options**:
   - Runtime types: `PrismaClientOptions` in `packages/client/src/runtime/getPrismaClient.ts`.
@@ -69,6 +71,7 @@
   - Tests rely on fixtures under `packages/**/src/__tests__/fixtures`; many now contain `prisma.config.ts`.
   - Default Jest/Vitest runner is invoked via `pnpm --filter @prisma/<pkg> test <pattern>`; it wraps `dotenv` and expects `.db.env`.
     - Some packages already use Vitest, `packages/cli` uses both for different tests as it's in the process of transition, older packages still use Jest.
+  - Functional generated clients in `packages/client/tests/functional/**/.generated` import `packages/client/runtime/client.js` directly; runtime changes in `src/runtime` may need corresponding runtime bundle updates to be exercised by functional tests.
   - Inline snapshots can be sensitive to formatting; prefer concise expectations unless the exact message matters.

 - **Environment loading**: Prisma 7 removes automatic `.env` loading.
diff --git a/packages/client/src/runtime/core/extensions/resolve-result-extension-context.ts b/packages/client/src/runtime/core/extensions/resolve-result-extension-context.ts
new file mode 100644
index 000000000000..c8468c521c22
--- /dev/null
+++ b/packages/client/src/runtime/core/extensions/resolve-result-extension-context.ts
@@ -0,0 +1,101 @@
+import { RuntimeDataModel } from '@prisma/client-common'
+
+import { JsArgs } from '../types/exported/JsApi'
+
+type ResolveResultExtensionContextParams = {
+  dataPath: string[]
+  modelName: string
+  args?: JsArgs
+  runtimeDataModel: RuntimeDataModel
+}
+
+type ResultExtensionContext = {
+  modelName: string
+  args: JsArgs
+}
+
+/**
+ * Resolves the model/args context used for result extensions from a query dataPath.
+ * Falls back to the root model context when traversal can not continue because the model is
+ * missing, the segment is not a relation, or the path format is invalid.
+ * Throws when a relation field segment from dataPath does not exist on the current model.
+ */
+export function resolveResultExtensionContext({
+  dataPath,
+  modelName,
+  args,
+  runtimeDataModel,
+}: ResolveResultExtensionContextParams): ResultExtensionContext {
+  const rootContext = {
+    modelName,
+    args: args ?? {},
+  }
+
+  const relationPath = relationPathFromDataPath(dataPath)
+  if (!relationPath || relationPath.length === 0) {
+    return rootContext
+  }
+
+  let currentModelName = modelName
+  let currentArgs: JsArgs = args ?? {}
+
+  for (const relationFieldName of relationPath) {
+    const currentModel = runtimeDataModel.models[currentModelName]
+    if (!currentModel) {
+      return rootContext
+    }
+
+    const relationField = currentModel.fields.find((field) => field.name === relationFieldName)
+    if (!relationField) {
+      throw new Error(
+        `Could not resolve relation field "${relationFieldName}" on model "${currentModelName}" from dataPath "${dataPath.join('.')}"`,
+      )
+    }
+    if (relationField.kind !== 'object' || !relationField.relationName) {
+      return rootContext
+    }
+
+    currentModelName = relationField.type
+    currentArgs = resolveNextArgs(currentArgs, relationFieldName)
+  }
+
+  return {
+    modelName: currentModelName,
+    args: currentArgs,
+  }
+}
+
+function relationPathFromDataPath(dataPath: string[]): string[] | undefined {
+  const relationPath: string[] = []
+
+  for (let index = 0; index < dataPath.length; index += 2) {
+    const selector = dataPath[index]
+    const relationFieldName = dataPath[index + 1]
+
+    if ((selector !== 'select' && selector !== 'include') || relationFieldName === undefined) {
+      return undefined
+    }
+
+    relationPath.push(relationFieldName)
+  }
+
+  return relationPath
+}
+
+function resolveNextArgs(args: JsArgs, relationFieldName: string): JsArgs {
+  const select = args.select?.[relationFieldName]
+  if (isNestedArgs(select)) {
+    return select
+  }
+
+  const include = args.include?.[relationFieldName]
+  if (isNestedArgs(include)) {
+    return include
+  }
+
+  return {}
+}
+
+function isNestedArgs(value: unknown): value is JsArgs {
+  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
+}
diff --git a/packages/client/src/runtime/getPrismaClient.ts b/packages/client/src/runtime/getPrismaClient.ts
index cab4c1426992..11f5d3df3687 100644
--- a/packages/client/src/runtime/getPrismaClient.ts
+++ b/packages/client/src/runtime/getPrismaClient.ts
@@ -20,6 +20,7 @@ import { $extends } from './core/extensions/$extends'
 import { applyAllResultExtensions } from './core/extensions/applyAllResultExtensions'
 import { applyQueryExtensions } from './core/extensions/applyQueryExtensions'
 import { MergedExtensionsList } from './core/extensions/MergedExtensionsList'
+import { resolveResultExtensionContext } from './core/extensions/resolve-result-extension-context'
 import { getEngineInstance } from './core/init/getEngineInstance'
 import { GlobalOmitOptions, serializeJsonQuery } from './core/jsonProtocol/serializeJsonQuery'
 import {
@@ -808,10 +809,18 @@ Or read our docs at https://www.prisma.io/docs/concepts/components/prisma-client
         if (!requestParams.model) {
           return result
         }
-        return applyAllResultExtensions({
-          result,
+
+        const extensionContext = resolveResultExtensionContext({
+          dataPath: requestParams.dataPath,
           modelName: requestParams.model,
           args: requestParams.args,
+          runtimeDataModel: this._runtimeDataModel,
+        })
+
+        return applyAllResultExtensions({
+          result,
+          modelName: extensionContext.modelName,
+          args: extensionContext.args,
           extensions: this._extensions,
           runtimeDataModel: this._runtimeDataModel,
           globalOmit: this._globalOmit,

PATCH

echo "Patch applied successfully."
