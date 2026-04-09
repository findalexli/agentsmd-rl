#!/bin/bash
set -e

cd /workspace/bun

# Check if patch already applied
if grep -q "cmpxchgWeak.*current.*continue" src/threading/ThreadPool.zig; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/src/threading/ThreadPool.zig b/src/threading/ThreadPool.zig
index 448f8dfdf3d..e116c20274a 100644
--- a/src/threading/ThreadPool.zig
+++ b/src/threading/ThreadPool.zig
@@ -327,23 +327,24 @@ pub const default_thread_stack_size = brk: {
 /// https://www.youtube.com/watch?v=ys3qcbO5KWw
 pub fn warm(self: *ThreadPool, count: u14) void {
     self.is_running.store(true, .monotonic);
+    const target = @min(count, @as(u14, @truncate(self.max_threads)));
     var sync = @as(Sync, @bitCast(self.sync.load(.monotonic)));
-    if (sync.spawned >= count)
-        return;
-
-    const to_spawn = @min(count - sync.spawned, @as(u14, @truncate(self.max_threads)));
-    while (sync.spawned < to_spawn) {
+    while (sync.spawned < target) {
         var new_sync = sync;
         new_sync.spawned += 1;
-        sync = @as(Sync, @bitCast(self.sync.cmpxchgWeak(
+        if (self.sync.cmpxchgWeak(
             @as(u32, @bitCast(sync)),
             @as(u32, @bitCast(new_sync)),
             .release,
             .monotonic,
-        ) orelse break));
-        const spawn_config = std.Thread.SpawnConfig{ .stack_size = default_thread_stack_size };
+        )) |current| {
+            sync = @as(Sync, @bitCast(current));
+            continue;
+        }
+        const spawn_config = std.Thread.SpawnConfig{ .stack_size = self.stack_size };
         const thread = std.Thread.spawn(spawn_config, Thread.run, .{self}) catch return self.unregister(null);
         thread.detach();
+        sync = new_sync;
     }
 }

@@ -384,7 +385,7 @@ noinline fn notifySlow(self: *ThreadPool, is_waking: bool) void {

             // We signaled to spawn a new thread
             if (can_wake and sync.spawned < self.max_threads) {
-                const spawn_config = std.Thread.SpawnConfig{ .stack_size = default_thread_stack_size };
+                const spawn_config = std.Thread.SpawnConfig{ .stack_size = self.stack_size };
                 const thread = std.Thread.spawn(spawn_config, Thread.run, .{self}) catch return self.unregister(null);
                 // if (self.name.len > 0) thread.setName(self.name) catch {};
                 return thread.detach();
PATCH

echo "Patch applied successfully"
