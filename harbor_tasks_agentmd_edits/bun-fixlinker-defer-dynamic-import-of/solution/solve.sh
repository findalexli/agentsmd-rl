#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'import_record.kind == .require or import_record.kind == .require_resolve or import_record.kind == .dynamic' src/linker.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the complete patch for all three files
git apply - <<'PATCH'
diff --git a/src/linker.zig b/src/linker.zig
index bae52a8f405..f9ce66257eb 100644
--- a/src/linker.zig
+++ b/src/linker.zig
@@ -222,7 +222,7 @@ pub const Linker = struct {

         if (comptime is_bun) {
             // make these happen at runtime
-            if (import_record.kind == .require or import_record.kind == .require_resolve) {
+            if (import_record.kind == .require or import_record.kind == .require_resolve or import_record.kind == .dynamic) {
                 return false;
             }
         }
diff --git a/src/logger.zig b/src/logger.zig
index 1214403e0a0..ab4f4e053ff 100644
--- a/src/logger.zig
+++ b/src/logger.zig
@@ -927,7 +927,9 @@ pub const Log = struct {
         err: anyerror,
     ) OOM!void {
         @branchHint(.cold);
-        return try addResolveErrorWithLevel(log, source, r, allocator, fmt, args, import_kind, false, .err, err);
+        // Always dupe the line_text from the source to ensure the Location data
+        // outlives the source's backing memory (which may be arena-allocated).
+        return try addResolveErrorWithLevel(log, source, r, allocator, fmt, args, import_kind, true, .err, err);
     }

     pub fn addResolveErrorWithTextDupe(
diff --git a/src/s3/credentials.zig b/src/s3/credentials.zig
index 162b7f18597..d6a8632611b 100644
--- a/src/s3/credentials.zig
+++ b/src/s3/credentials.zig
@@ -1165,7 +1165,7 @@ const CanonicalRequest = struct {
 /// Returns true if the given slice contains any CR (\r) or LF (\n) characters,
 /// which would allow HTTP header injection if used in a header value.
 fn containsNewlineOrCR(value: []const u8) bool {
-    return std.mem.indexOfAny(u8, value, "\r\n") != null;
+    return strings.indexOfAny(value, "\r\n") != null;
 }

 const std = @import("std");
PATCH

# Create regression test directory and file
mkdir -p test/regression/issue
cat > test/regression/issue/25707.test.ts << 'REGTEST'
import { expect, test } from "bun:test";
import { bunEnv, bunExe, tempDir } from "harness";

// https://github.com/oven-sh/bun/issues/25707
// Dynamic import() of non-existent node: modules inside CJS files should not
// fail at transpile/require time. They should be deferred to runtime so that
// try/catch can handle the error gracefully.

test("require() of CJS file containing dynamic import of non-existent node: module does not fail at load time", async () => {
  using dir = tempDir("issue-25707", {
    // Simulates turbopack-generated chunks: a CJS module with a factory function
    // containing import("node:sqlite") inside a try/catch that is never called
    // during require().
    "chunk.js": `
      module.exports = [
        function factory(exports) {
          async function detect(e) {
            if ("createSession" in e) {
              let c;
              try {
                ({DatabaseSync: c} = await import("node:sqlite"))
              } catch(a) {
                if (null !== a && "object" == typeof a && "code" in a && "ERR_UNKNOWN_BUILTIN_MODULE" !== a.code)
                  throw a;
              }
            }
          }
          exports.detect = detect;
        }
      ];
    `,
    "main.js": `
      // This require() should not fail even though chunk.js contains import("node:sqlite")
      const factories = require("./chunk.js");
      console.log("loaded " + factories.length + " factories");
    `,
  });

  await using proc = Bun.spawn({
    cmd: [bunExe(), "main.js"],
    cwd: String(dir),
    env: bunEnv,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr, exitCode] = await Promise.all([proc.stdout.text(), proc.stderr.text(), proc.exited]);

  expect(stdout.trim()).toBe("loaded 1 factories");
  expect(exitCode).toBe(0);
});

test("require() of CJS file with bare dynamic import of non-existent node: module does not fail at load time", async () => {
  // The dynamic import is NOT inside a try/catch, but it's still a dynamic import
  // that should only be resolved at runtime, not at transpile time
  using dir = tempDir("issue-25707-bare", {
    "lib.js": `
      module.exports = async function() {
        const { DatabaseSync } = await import("node:sqlite");
        return DatabaseSync;
      };
    `,
    "main.js": `
      const fn = require("./lib.js");
      console.log("loaded");
    `,
  });

  await using proc = Bun.spawn({
    cmd: [bunExe(), "main.js"],
    cwd: String(dir),
    env: bunEnv,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr, exitCode] = await Promise.all([proc.stdout.text(), proc.stderr.text(), proc.exited]);

  expect(stdout.trim()).toBe("loaded");
  expect(exitCode).toBe(0);
});

test("dynamic import of non-existent node: module in CJS rejects at runtime with correct error", async () => {
  using dir = tempDir("issue-25707-runtime", {
    "lib.js": `
      module.exports = async function() {
        try {
          const { DatabaseSync } = await import("node:sqlite");
          return "resolved";
        } catch (e) {
          return "caught: " + e.code;
        }
      };
    `,
    "main.js": `
      const fn = require("./lib.js");
      fn().then(result => console.log(result));
    `,
  });

  await using proc = Bun.spawn({
    cmd: [bunExe(), "main.js"],
    cwd: String(dir),
    env: bunEnv,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr, exitCode] = await Promise.all([proc.stdout.text(), proc.stderr.text(), proc.exited]);

  expect(stdout.trim()).toBe("caught: ERR_UNKNOWN_BUILTIN_MODULE");
  expect(exitCode).toBe(0);
});
REGTEST

echo "Patch applied successfully."
