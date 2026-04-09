#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'statxFallback' src/sys.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'PATCH'
diff --git a/src/sys.zig b/src/sys.zig
index 044e7965177..eca2555e9ba 100644
--- a/src/sys.zig
+++ b/src/sys.zig
@@ -587,6 +587,22 @@ inline fn makedev(major: u32, minor: u32) u64 {
     return (maj << 8) | (min & 0xFF) | ((min & 0xFFF00) << 12);
 }

+fn statxFallback(fd: bun.FileDescriptor, path: ?[*:0]const u8, flags: u32) Maybe(PosixStat) {
+    if (path) |p| {
+        const path_span = bun.span(p);
+        const fallback = if (flags & linux.AT.SYMLINK_NOFOLLOW != 0) lstat(path_span) else stat(path_span);
+        return switch (fallback) {
+            .result => |s| .{ .result = PosixStat.init(&s) },
+            .err => |e| .{ .err = e },
+        };
+    } else {
+        return switch (fstat(fd)) {
+            .result => |s| .{ .result = PosixStat.init(&s) },
+            .err => |e| .{ .err = e },
+        };
+    }
+}
+
 fn statxImpl(fd: bun.FileDescriptor, path: ?[*:0]const u8, flags: u32, mask: u32) Maybe(PosixStat) {
     if (comptime !Environment.isLinux) {
         @compileError("statx is only supported on Linux");
@@ -597,29 +613,33 @@ fn statxImpl(fd: bun.FileDescriptor, path: ?[*:0]const u8, flags: u32, mask: u32
     while (true) {
         const rc = linux.statx(@intCast(fd.cast()), if (path) |p| p else "", flags, mask, &buf);

+        // On some setups (QEMU user-mode, S390 RHEL docker), statx returns a
+        // positive value other than 0 with errno unset — neither a normal
+        // success (0) nor a kernel -errno. Treat as "not implemented".
+        // See nodejs/node#27275 and libuv/libuv src/unix/fs.c.
+        if (@as(isize, @bitCast(rc)) > 0) {
+            supports_statx_on_linux.store(false, .monotonic);
+            return statxFallback(fd, path, flags);
+        }
+
         if (Maybe(PosixStat).errnoSys(rc, .statx)) |err| {
             // Retry on EINTR
             if (err.getErrno() == .INTR) continue;

-            // Handle unsupported statx by setting flag and falling back
-            if (err.getErrno() == .NOSYS or err.getErrno() == .OPNOTSUPP) {
-                supports_statx_on_linux.store(false, .monotonic);
-                if (path) |p| {
-                    const path_span = bun.span(p);
-                    const fallback = if (flags & linux.AT.SYMLINK_NOFOLLOW != 0) lstat(path_span) else stat(path_span);
-                    return switch (fallback) {
-                        .result => |s| .{ .result = PosixStat.init(&s) },
-                        .err => |e| .{ .err = e },
-                    };
-                } else {
-                    return switch (fstat(fd)) {
-                        .result => |s| .{ .result = PosixStat.init(&s) },
-                        .err => |e| .{ .err = e },
-                    };
-                }
+            // Handle unsupported statx by setting the flag and falling back.
+            // Fall back on the same errnos libuv does (deps/uv/src/unix/fs.c):
+            //   ENOSYS:     kernel < 4.11
+            //   EOPNOTSUPP: filesystem doesn't support it
+            //   EPERM:      seccomp filter rejects statx (libseccomp < 2.3.3,
+            //               docker < 18.04, various CI sandboxes)
+            //   EINVAL:     old Android builds
+            switch (err.getErrno()) {
+                .NOSYS, .OPNOTSUPP, .PERM, .INVAL => {
+                    supports_statx_on_linux.store(false, .monotonic);
+                    return statxFallback(fd, path, flags);
+                },
+                else => return err,
             }
-
-            return err;
         }

         // Convert statx buffer to PosixStat structure

PATCH

echo "Patch applied successfully."
