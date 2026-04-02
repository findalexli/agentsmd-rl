#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

TARGET="test/js/bun/http/serve-body-leak.test.ts"

# Idempotency: check if already fixed
if grep -q 'isASAN' "$TARGET"; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/js/bun/http/serve-body-leak.test.ts b/test/js/bun/http/serve-body-leak.test.ts
index b10078fa082..7f94b2ccd2b 100644
--- a/test/js/bun/http/serve-body-leak.test.ts
+++ b/test/js/bun/http/serve-body-leak.test.ts
@@ -1,5 +1,5 @@
 import { expect, it } from "bun:test";
-import { bunEnv, bunExe, isCI, isDebug, isFlaky, isLinux, isWindows } from "harness";
+import { bunEnv, bunExe, isASAN, isCI, isDebug, isFlaky, isLinux, isWindows } from "harness";
 import { join } from "path";

 const payload = Buffer.alloc(512 * 1024, "1").toString("utf-8"); // decent size payload to test memory leak
@@ -153,6 +153,10 @@ async function calculateMemoryLeak(fn: (url: URL) => Promise<void>, url: URL) {
 // Since the payload size is 512 KB
 // If it was leaking the body, the memory usage would be at least 512 KB * 10_000 = 5 GB
 // If it ends up around 280 MB, it's probably not leaking the body.
+//
+// Skip on ASAN: its quarantine (default 256MB) and allocator metadata inflate
+// RSS enough to break the `end_memory ≤ 512MB` threshold even without leaks,
+// and the 2x slowdown can hit the 40/60s timeout with 20k requests per case.
 for (const test_info of [
   ["#10265 should not leak memory when ignoring the body", callIgnore, false, 64],
   ["should not leak memory when buffering the body", callBuffering, false, 64],
@@ -163,7 +167,7 @@ for (const test_info of [
   ["should not leak memory when streaming the body and echoing it back", callStreamingEcho, false, 64],
 ] as const) {
   const [testName, fn, skip, maxMemoryGrowth] = test_info;
-  it.todoIf(skip || (isFlaky && isWindows))(
+  it.todoIf(skip || (isFlaky && isWindows) || isASAN)(
     testName,
     async () => {
       const { url, process } = await getURL();

PATCH

echo "Patch applied successfully."
