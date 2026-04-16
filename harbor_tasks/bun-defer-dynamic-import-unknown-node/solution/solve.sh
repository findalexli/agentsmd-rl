#!/bin/bash
set -e

cd /workspace/bun

# Apply the gold patch for PR #26981
# This includes:
# 1. Code fix in src/linker.zig (defer dynamic import() to runtime)
# 2. Bugfix in src/logger.zig (use-after-poison fix)
# 3. Refactor in src/s3/credentials.zig (use bun.strings instead of std.mem)
# 4. Config update in src/CLAUDE.md (formatting improvements)
# 5. Test file in test/regression/issue/25707.test.ts

patch -p1 << 'ENDOFPATCH'
diff --git a/src/CLAUDE.md b/src/CLAUDE.md
index 86586f0b15f..17910ec2772 100644
--- a/src/CLAUDE.md
+++ b/src/CLAUDE.md
@@ -15,16 +15,16 @@ Conventions:

 **Always use `bun.*` APIs instead of `std.*`.** The `bun` namespace (`@import("bun")`) provides cross-platform wrappers that preserve OS error info and never use `unreachable`. Using `std.fs`, `std.posix`, or `std.os` directly is wrong in this codebase.

-| Instead of | Use |
-|-----------|-----|
-| `std.fs.File` | `bun.sys.File` |
-| `std.fs.cwd()` | `bun.FD.cwd()` |
-| `std.posix.open/read/write/stat/mkdir/unlink/rename/symlink` | `bun.sys.*` equivalents |
-| `std.fs.path.join/dirname/basename` | `bun.path.join/dirname/basename` |
-| `std.mem.eql/indexOf/startsWith` (for strings) | `bun.strings.eql/indexOf/startsWith` |
-| `std.posix.O` / `std.posix.mode_t` / `std.posix.fd_t` | `bun.O` / `bun.Mode` / `bun.FD` |
-| `std.process.Child` | `bun.spawnSync` |
-| `catch bun.outOfMemory()` | `bun.handleOom(...)` |
+| Instead of                                                   | Use                                  |
+| ------------------------------------------------------------ | ------------------------------------ |
+| `std.fs.File`                                                | `bun.sys.File`                       |
+| `std.fs.cwd()`                                               | `bun.FD.cwd()`                       |
+| `std.posix.open/read/write/stat/mkdir/unlink/rename/symlink` | `bun.sys.*` equivalents              |
+| `std.fs.path.join/dirname/basename`                          | `bun.path.join/dirname/basename`     |
+| `std.mem.eql/indexOf/startsWith` (for strings)               | `bun.strings.eql/indexOf/startsWith` |
+| `std.posix.O` / `std.posix.mode_t` / `std.posix.fd_t`        | `bun.O` / `bun.Mode` / `bun.FD`      |
+| `std.process.Child`                                          | `bun.spawnSync`                      |
+| `catch bun.outOfMemory()`                                    | `bun.handleOom(...)`                 |

 ## `bun.sys` — System Calls (`src/sys.zig`)

@@ -39,6 +39,7 @@ const fd = switch (bun.sys.open(path, bun.O.RDONLY, 0)) {
 ```

 Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):
+
 - `open`, `openat`, `openA` (non-sentinel) → `Maybe(bun.FileDescriptor)`
 - `read`, `readAll`, `pread` → `Maybe(usize)`
 - `write`, `pwrite`, `writev` → `Maybe(usize)`
@@ -68,6 +69,7 @@ switch (bun.sys.File.writeFile(bun.FD.cwd(), path, data)) {
 ```

 Key methods:
+
 - `File.open/openat/makeOpen` → `Maybe(File)` (`makeOpen` creates parent dirs)
 - `file.read/readAll/write/writeAll` — single or looped I/O
 - `file.readToEnd(allocator)` — read entire file into allocated buffer
@@ -169,6 +171,7 @@ bun.path.z(path, &buf)  // returns [:0]const u8
 Use `bun.PathBuffer` for path buffers: `var buf: bun.PathBuffer = undefined;`

 For pooled path buffers (avoids 64KB stack allocations on Windows):
+
 ```zig
 const buf = bun.path_buffer_pool.get();
 defer bun.path_buffer_pool.put(buf);
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
@@ -1162,7 +1162,7 @@ const CanonicalRequest = struct {
 /// Returns true if the given slice contains any CR (\r) or LF (\n) characters,
 /// which would allow HTTP header injection if used in a header value.
 fn containsNewlineOrCR(value: []const u8) bool {
-    return std.mem.indexOfAny(u8, value, "\r\n") != null;
+    return strings.indexOfAny(value, "\r\n") != null;
 }

 const std = @import("std");
ENDOFPATCH

# Create the test file
mkdir -p test/regression/issue
cat > test/regression/issue/25707.test.ts << 'ENDOFTEST'
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
ENDOFTEST

echo "Gold patch applied successfully"
