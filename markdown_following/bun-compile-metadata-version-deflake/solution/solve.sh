#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if the for-loop over invalidVersions is already removed, skip
if ! grep -q 'for.*of.*invalidVersions' test/bundler/compile-windows-metadata.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/bundler/compile-windows-metadata.test.ts b/test/bundler/compile-windows-metadata.test.ts
index d7ddb5e543c..3bab5efd518 100644
--- a/test/bundler/compile-windows-metadata.test.ts
+++ b/test/bundler/compile-windows-metadata.test.ts
@@ -322,39 +322,35 @@ describe.skipIf(!isWindows).concurrent("Windows compile metadata", () => {
       expect(version).toBe(expected);
     });

-    test("invalid version format should error gracefully", async () => {
+    test.each([
+      { version: "not.a.version" },
+      { version: "1.2.3.4.5" },
+      { version: "1.-2.3.4" },
+      { version: "65536.0.0.0" }, // > 65535
+      { version: "" },
+    ])("invalid version format should error gracefully: $version", async ({ version }) => {
       using dir = tempDir("windows-invalid-version", {
         "app.js": `console.log("Invalid version test");`,
       });

-      const invalidVersions = [
-        "not.a.version",
-        "1.2.3.4.5",
-        "1.-2.3.4",
-        "65536.0.0.0", // > 65535
-        "",
-      ];
-
-      for (const version of invalidVersions) {
-        await using proc = Bun.spawn({
-          cmd: [
-            bunExe(),
-            "build",
-            "--compile",
-            join(String(dir), "app.js"),
-            "--outfile",
-            join(String(dir), "test.exe"),
-            "--windows-version",
-            version,
-          ],
-          env: bunEnv,
-          stdout: "pipe",
-          stderr: "pipe",
-        });
-
-        const exitCode = await proc.exited;
-        expect(exitCode).not.toBe(0);
-      }
+      await using proc = Bun.spawn({
+        cmd: [
+          bunExe(),
+          "build",
+          "--compile",
+          join(String(dir), "app.js"),
+          "--outfile",
+          join(String(dir), "test.exe"),
+          "--windows-version",
+          version,
+        ],
+        env: bunEnv,
+        stdout: "pipe",
+        stderr: "pipe",
+      });
+
+      const exitCode = await proc.exited;
+      expect(exitCode).not.toBe(0);
     });
   });

PATCH
