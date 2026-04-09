#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if grep -q '} finally {' packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts b/packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts
index c7f1bac97e..f0c2d1252b 100644
--- a/packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts
+++ b/packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts
@@ -46,13 +46,15 @@ async function runInRunnerObject(
 	const id = nextCallbackId++;
 	pendingCallbacks.set(id, callback);

-	const stub = env.__VITE_RUNNER_OBJECT__.get("singleton");
-	await stub.executeCallback(id);
+	try {
+		const stub = env.__VITE_RUNNER_OBJECT__.get("singleton");
+		await stub.executeCallback(id);

-	const result = callbackResults.get(id);
-	callbackResults.delete(id);
-
-	return result;
+		return callbackResults.get(id);
+	} finally {
+		pendingCallbacks.delete(id);
+		callbackResults.delete(id);
+	}
 }

 /**
@@ -152,7 +154,6 @@ export class __VITE_RUNNER_OBJECT__ extends DurableObject<WrapperEnv> {
 	 */
 	async executeCallback(id: number): Promise<void> {
 		const callback = pendingCallbacks.get(id);
-		pendingCallbacks.delete(id);

 		if (!callback) {
 			throw new Error(`No pending callback with id ${id}`);

PATCH

echo "Patch applied successfully."
