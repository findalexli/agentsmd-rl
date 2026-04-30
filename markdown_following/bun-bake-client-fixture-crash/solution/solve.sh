#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if retry logic already exists in loadPage, patch is applied
if grep -q 'maxRetries' test/bake/client-fixture.mjs 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/test/bake/bake-harness.ts b/test/bake/bake-harness.ts
index 9d1b99472a9..57855b2ccfa 100644
--- a/test/bake/bake-harness.ts
+++ b/test/bake/bake-harness.ts
@@ -817,6 +817,7 @@ export class Client extends EventEmitter {
     this.#proc = proc;
     this.hmr = options.hmr;
     this.output = new OutputLineStream("web", proc.stdout, proc.stderr);
+    proc.exited.then(exitCode => (this.output.exitCode = exitCode));
   }

   hardReload(options: { errors?: ErrorSpec[] } = {}) {
diff --git a/test/bake/client-fixture.mjs b/test/bake/client-fixture.mjs
index 39f39686703..4010e44fd31 100644
--- a/test/bake/client-fixture.mjs
+++ b/test/bake/client-fixture.mjs
@@ -6,6 +6,12 @@ import assert from "node:assert/strict";
 import util from "node:util";
 import { exitCodeMap } from "./exit-code-map.mjs";

+// Prevent silent crashes from unhandled promise rejections
+process.on("unhandledRejection", reason => {
+  console.error("[E] Unhandled rejection:", reason);
+  process.exit(exitCodeMap.reloadFailed);
+});
+
 const args = process.argv.slice(2);
 let url = args.find(arg => !arg.startsWith("-"));
 if (!url) {
@@ -344,13 +350,29 @@ async function handleReload() {

 // Extract page loading logic to a reusable function
 async function loadPage() {
-  const response = await fetch(url);
+  let response;
+  const maxRetries = 3;
+  for (let attempt = 0; attempt < maxRetries; attempt++) {
+    try {
+      response = await fetch(url);
+      break;
+    } catch (err) {
+      if (attempt < maxRetries - 1) {
+        // Retry after a short delay for transient connection errors (e.g. Windows port not ready)
+        await new Promise(resolve => setTimeout(resolve, 100 * (attempt + 1)));
+        continue;
+      }
+      console.error("Failed to fetch page after retries:", err.message);
+      process.exit(exitCodeMap.reloadFailed);
+    }
+  }
   if (response.status >= 400 && response.status <= 499) {
     console.error("Failed to load page:", response.statusText);
     process.exit(exitCodeMap.reloadFailed);
   }
-  if (!response.headers.get("content-type").match(/^text\/html;?/)) {
-    console.error("Invalid content type:", response.headers.get("content-type"));
+  const contentType = response.headers.get("content-type");
+  if (!contentType || !contentType.match(/^text\/html;?/)) {
+    console.error("Invalid content type:", contentType);
     process.exit(exitCodeMap.reloadFailed);
   }
   const html = await response.text();
@@ -540,4 +562,9 @@ process.on("exit", () => {

 // Initial page load
 createWindow(url);
-await loadPage(window);
+try {
+  await loadPage(window);
+} catch (error) {
+  console.error("Failed initial page load:", error);
+  process.exit(exitCodeMap.reloadFailed);
+}

PATCH

echo "Patch applied successfully."
