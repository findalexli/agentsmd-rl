#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if fix is already applied, skip
if grep -q 'security scanner failed:' src/install/PackageManager/install_with_manager.zig 2>/dev/null; then
    echo "Fix already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/install/PackageManager/install_with_manager.zig b/src/install/PackageManager/install_with_manager.zig
index bb533941580..f767dacb1d8 100644
--- a/src/install/PackageManager/install_with_manager.zig
+++ b/src/install/PackageManager/install_with_manager.zig
@@ -643,9 +643,29 @@ pub fn installWithManager(
                 if (security_scanner.performSecurityScanAfterResolution(manager, ctx, original_cwd) catch |err| {
                     switch (err) {
                         error.SecurityScannerInWorkspace => {
-                            Output.pretty("<red>Security scanner cannot be a dependency of a workspace package. It must be a direct dependency of the root package.<r>\n", .{});
+                            Output.errGeneric("security scanner cannot be a dependency of a workspace package. It must be a direct dependency of the root package.", .{});
+                        },
+                        error.SecurityScannerRetryFailed => {
+                            Output.errGeneric("security scanner failed after partial install. This is probably a bug in Bun. Please report it at https://github.com/oven-sh/bun/issues", .{});
+                        },
+                        error.InvalidPackageID => {
+                            Output.errGeneric("cannot perform partial install: security scanner package ID is invalid", .{});
+                        },
+                        error.PartialInstallFailed => {
+                            Output.errGeneric("failed to install security scanner package", .{});
+                        },
+                        error.NoPackagesInstalled => {
+                            Output.errGeneric("no packages were installed during security scanner installation", .{});
+                        },
+                        error.IPCPipeFailed => {
+                            Output.errGeneric("failed to create IPC pipe for security scanner", .{});
+                        },
+                        error.ProcessWatchFailed => {
+                            Output.errGeneric("failed to watch security scanner process", .{});
+                        },
+                        else => |e| {
+                            Output.errGeneric("security scanner failed: {s}", .{@errorName(e)});
                         },
-                        else => {},
                     }

                     Global.exit(1);
diff --git a/src/install/PackageManager/security_scanner.zig b/src/install/PackageManager/security_scanner.zig
index fbd6285dc9d..3fff26a3671 100644
--- a/src/install/PackageManager/security_scanner.zig
+++ b/src/install/PackageManager/security_scanner.zig
@@ -60,7 +60,6 @@ pub fn doPartialInstallOfSecurityScanner(
     }

     if (security_scanner_pkg_id == invalid_package_id) {
-        Output.errGeneric("Cannot perform partial install: security scanner package ID is invalid", .{});
         return error.InvalidPackageID;
     }

@@ -93,12 +92,10 @@ pub fn doPartialInstallOfSecurityScanner(
     }

     if (summary.fail > 0) {
-        Output.errGeneric("Failed to install security scanner package (failed: {d}, success: {d})", .{ summary.fail, summary.success });
         return error.PartialInstallFailed;
     }

     if (summary.success == 0 and summary.skipped == 0) {
-        Output.errGeneric("No packages were installed during security scanner installation", .{});
         return error.NoPackagesInstalled;
     }
 }
@@ -155,7 +152,6 @@ const ScannerFinder = struct {
                 const dep = this.manager.lockfile.buffers.dependencies.items[dep_id];

                 if (std.mem.eql(u8, dep.name.slice(string_buf), this.scanner_name)) {
-                    Output.errGeneric("Security scanner '{s}' cannot be a dependency of a workspace package. It must be a direct dependency of the root package.", .{this.scanner_name});
                     return error.SecurityScannerInWorkspace;
                 }
             }
@@ -183,7 +179,8 @@ pub fn performSecurityScanAfterResolution(manager: *PackageManager, command_ctx:
             const retry_result = try attemptSecurityScanWithRetry(manager, security_scanner, scan_all, command_ctx, original_cwd, true);
             switch (retry_result) {
                 .success => |scan_results| return scan_results,
-                else => return error.SecurityScannerRetryFailed,
+                .needs_install => return error.SecurityScannerRetryFailed,
+                .@"error" => |err| return err,
             }
         },
         .@"error" => |err| return err,
@@ -204,11 +201,7 @@ pub fn performSecurityScanForAll(manager: *PackageManager, command_ctx: bun.cli.
             const retry_result = try attemptSecurityScanWithRetry(manager, security_scanner, true, command_ctx, original_cwd, true);
             switch (retry_result) {
                 .success => |scan_results| return scan_results,
-                .needs_install => {
-                    // Should not happen after retry - we just installed it
-                    Output.errGeneric("Security scanner still required installation after partial install. This is probably a bug in Bun. Please report it to https://github.com/oven-sh/bun/issues", .{});
-                    return error.SecurityScannerRetryFailed;
-                },
+                .needs_install => return error.SecurityScannerRetryFailed,
                 .@"error" => |err| return err,
             }
         },
diff --git a/test/regression/issue/28193.test.ts b/test/regression/issue/28193.test.ts
new file mode 100644
index 00000000000..c7027de72bf
--- /dev/null
+++ b/test/regression/issue/28193.test.ts
@@ -0,0 +1,56 @@
+import { expect, test } from "bun:test";
+import { bunEnv, bunExe, tempDir } from "harness";
+
+test("bun install prints error when security scanner is unavailable", async () => {
+  using dir = tempDir("issue-28193", {
+    "package.json": JSON.stringify({
+      name: "test-28193",
+      dependencies: {
+        "is-even": "1.0.0",
+      },
+    }),
+    "bunfig.toml": `[install.security]\nscanner = "@nonexistent-scanner/does-not-exist"\n`,
+  });
+
+  await using proc = Bun.spawn({
+    cmd: [bunExe(), "install"],
+    env: { ...bunEnv, BUN_INSTALL_CACHE_DIR: String(dir) + "/.cache" },
+    cwd: String(dir),
+    stdout: "pipe",
+    stderr: "pipe",
+  });
+
+  const [stdout, stderr, exitCode] = await Promise.all([proc.stdout.text(), proc.stderr.text(), proc.exited]);
+
+  // Should print an error message about the scanner failure, not exit silently
+  expect(stderr).toContain("security scanner");
+  expect(exitCode).toBe(1);
+}, 30_000);
+
+test("bun install prints error when scanner package is invalid", async () => {
+  // When the scanner is a devDependency but not a valid scanner module,
+  // the install should fail with a clear error message
+  using dir = tempDir("issue-28193-invalid", {
+    "package.json": JSON.stringify({
+      name: "test-28193-invalid",
+      devDependencies: {
+        "is-even": "1.0.0",
+      },
+    }),
+    "bunfig.toml": `[install.security]\nscanner = "is-even"\n`,
+  });
+
+  await using proc = Bun.spawn({
+    cmd: [bunExe(), "install"],
+    env: { ...bunEnv, BUN_INSTALL_CACHE_DIR: String(dir) + "/.cache" },
+    cwd: String(dir),
+    stdout: "pipe",
+    stderr: "pipe",
+  });
+
+  const [stdout, stderr, exitCode] = await Promise.all([proc.stdout.text(), proc.stderr.text(), proc.exited]);
+
+  // Should print an error about the scanner, not exit silently
+  expect(stderr).toContain("security scanner");
+  expect(exitCode).toBe(1);
+}, 30_000);

PATCH

echo "Patch applied successfully."
