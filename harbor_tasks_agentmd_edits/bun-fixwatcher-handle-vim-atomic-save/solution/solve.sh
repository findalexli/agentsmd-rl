#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'addFileByPathSlow' src/Watcher.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/src/CLAUDE.md b/src/CLAUDE.md
index 65a333434d6..21b296e7f11 100644
--- a/src/CLAUDE.md
+++ b/src/CLAUDE.md
@@ -7,6 +7,6 @@ Syntax reminders:
 
 Conventions:
 
-- Prefer `@import` at the **bottom** of the file.
-- It's `@import("bun")` not `@import("root").bun`
+- Prefer `@import` at the **bottom** of the file, but the auto formatter will move them so you don't need to worry about it.
+- Prefer `@import("bun")`. Not `@import("root").bun` or `@import("../bun.zig")`.
 - You must be patient with the build.
diff --git a/src/Watcher.zig b/src/Watcher.zig
index 310acf364a5..bc17c7d11a7 100644
--- a/src/Watcher.zig
+++ b/src/Watcher.zig
@@ -312,6 +312,48 @@ fn watchLoop(this: *Watcher) bun.sys.Maybe(void) {
     return .success;
 }
 
+/// Register a file descriptor with kqueue on macOS without validation.
+///
+/// Preconditions (caller must ensure):
+/// - `fd` is a valid, open file descriptor
+/// - `fd` is not already registered with this kqueue
+/// - `watchlist_id` matches the entry's index in the watchlist
+///
+/// Note: This function does not propagate kevent registration errors.
+/// If registration fails, the file will not be watched but no error is returned.
+pub fn addFileDescriptorToKQueueWithoutChecks(this: *Watcher, fd: bun.FileDescriptor, watchlist_id: usize) void {
+    const KEvent = std.c.Kevent;
+
+    // https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/kqueue.2.html
+    var event = std.mem.zeroes(KEvent);
+
+    event.flags = std.c.EV.ADD | std.c.EV.CLEAR | std.c.EV.ENABLE;
+    // we want to know about the vnode
+    event.filter = std.c.EVFILT.VNODE;
+
+    event.fflags = std.c.NOTE.WRITE | std.c.NOTE.RENAME | std.c.NOTE.DELETE;
+
+    // id
+    event.ident = @intCast(fd.native());
+
+    // Store the index for fast filtering later
+    event.udata = @as(usize, @intCast(watchlist_id));
+    var events: [1]KEvent = .{event};
+
+    // This took a lot of work to figure out the right permutation
+    // Basically:
+    // - We register the event here.
+    // our while(true) loop above receives notification of changes to any of the events created here.
+    _ = std.posix.system.kevent(
+        this.platform.fd.unwrap().?.native(),
+        @as([]KEvent, events[0..1]).ptr,
+        1,
+        @as([]KEvent, events[0..1]).ptr,
+        0,
+        null,
+    );
+}
+
 fn appendFileAssumeCapacity(
     this: *Watcher,
     fd: bun.FileDescriptor,
@@ -350,36 +392,7 @@ fn appendFileAssumeCapacity(
     };
 
     if (comptime Environment.isMac) {
-        const KEvent = std.c.Kevent;
-
-        // https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/kqueue.2.html
-        var event = std.mem.zeroes(KEvent);
-
-        event.flags = std.c.EV.ADD | std.c.EV.CLEAR | std.c.EV.ENABLE;
-        // we want to know about the vnode
-        event.filter = std.c.EVFILT.VNODE;
-
-        event.fflags = std.c.NOTE.WRITE | std.c.NOTE.RENAME | std.c.NOTE.DELETE;
-
-        // id
-        event.ident = @intCast(fd.native());
-
-        // Store the hash for fast filtering later
-        event.udata = @as(usize, @intCast(watchlist_id));
-        var events: [1]KEvent = .{event};
-
-        // This took a lot of work to figure out the right permutation
-        // Basically:
-        // - We register the event here.
-        // our while(true) loop above receives notification of changes to any of the events created here.
-        _ = std.posix.system.kevent(
-            this.platform.fd.unwrap().?.native(),
-            @as([]KEvent, events[0..1]).ptr,
-            1,
-            @as([]KEvent, events[0..1]).ptr,
-            0,
-            null,
-        );
+        this.addFileDescriptorToKQueueWithoutChecks(fd, watchlist_id);
     } else if (comptime Environment.isLinux) {
         // var file_path_to_use_ = std.mem.trimRight(u8, file_path_, "/");
         // var buf: [bun.MAX_PATH_BYTES+1]u8 = undefined;
@@ -612,6 +625,78 @@ pub fn addDirectory(
     return this.appendDirectoryAssumeCapacity(fd, file_path, hash, clone_file_path);
 }
 
+/// Lazily watch a file by path (slow path).
+///
+/// This function is used when a file needs to be watched but was not
+/// encountered during the normal import graph traversal. On macOS, it
+/// opens a file descriptor with O_EVTONLY to obtain an inode reference.
+///
+/// Thread-safe: uses internal locking to prevent race conditions.
+///
+/// Returns:
+/// - true if the file is successfully added to the watchlist or already watched
+/// - false if the file cannot be opened or added to the watchlist
+pub fn addFileByPathSlow(
+    this: *Watcher,
+    file_path: string,
+    loader: options.Loader,
+) bool {
+    if (file_path.len == 0) return false;
+    const hash = getHash(file_path);
+
+    // Check if already watched (with lock to avoid race with removal)
+    {
+        this.mutex.lock();
+        const already_watched = this.indexOf(hash) != null;
+        this.mutex.unlock();
+
+        if (already_watched) {
+            return true;
+        }
+    }
+
+    // Only open fd if we might need it
+    var fd: bun.FileDescriptor = bun.invalid_fd;
+    if (Environment.isMac) {
+        const path_z = std.posix.toPosixPath(file_path) catch return false;
+        switch (bun.sys.open(&path_z, bun.c.O_EVTONLY, 0)) {
+            .result => |opened| fd = opened,
+            .err => return false,
+        }
+    }
+
+    const res = this.addFile(fd, file_path, hash, loader, bun.invalid_fd, null, true);
+    switch (res) {
+        .result => {
+            // On macOS, addFile may have found the file already watched (race)
+            // and returned success without using our fd. Close it if unused.
+            if ((comptime Environment.isMac) and fd.isValid()) {
+                this.mutex.lock();
+                const maybe_idx = this.indexOf(hash);
+                const stored_fd = if (maybe_idx) |idx|
+                    this.watchlist.items(.fd)[idx]
+                else
+                    bun.invalid_fd;
+                this.mutex.unlock();
+
+                // Only close if entry exists and stored fd differs from ours.
+                // Race scenarios:
+                // 1. Entry removed (maybe_idx == null): our fd was stored then closed by flushEvictions → don't close
+                // 2. Entry exists with different fd: another thread added entry, addFile didn't use our fd → close ours
+                // 3. Entry exists with same fd: our fd was stored → don't close
+                if (maybe_idx != null and stored_fd.native() != fd.native()) {
+                    fd.close();
+                }
+            }
+            return true;
+        },
+        .err => {
+            if (fd.isValid()) fd.close();
+            return false;
+        },
+    }
+}
+
 pub fn addFile(
     this: *Watcher,
     fd: bun.FileDescriptor,
diff --git a/src/bun.js.zig b/src/bun.js.zig
index fb59390ea07..e6e171d8007 100644
--- a/src/bun.js.zig
+++ b/src/bun.js.zig
@@ -311,8 +311,8 @@ pub const Run = struct {
         }
 
         switch (this.ctx.debug.hot_reload) {
-            .hot => jsc.hot_reloader.HotReloader.enableHotModuleReloading(vm),
-            .watch => jsc.hot_reloader.WatchReloader.enableHotModuleReloading(vm),
+            .hot => jsc.hot_reloader.HotReloader.enableHotModuleReloading(vm, this.entry_path),
+            .watch => jsc.hot_reloader.WatchReloader.enableHotModuleReloading(vm, this.entry_path),
             else => {},
         }
 
@@ -328,6 +328,7 @@ pub const Run = struct {
                 promise.setHandled(vm.global.vm());
 
                 if (vm.hot_reload != .none or handled) {
+                    vm.addMainToWatcherIfNeeded();
                     vm.eventLoop().tick();
                     vm.eventLoop().tickPossiblyForever();
                 } else {
@@ -389,21 +390,21 @@ pub const Run = struct {
 
         {
             if (this.vm.isWatcherEnabled()) {
-                vm.handlePendingInternalPromiseRejection();
+                vm.reportExceptionInHotReloadedModuleIfNeeded();
 
                 while (true) {
                     while (vm.isEventLoopAlive()) {
                         vm.tick();
 
                         // Report exceptions in hot-reloaded modules
-                        vm.handlePendingInternalPromiseRejection();
+                        vm.reportExceptionInHotReloadedModuleIfNeeded();
 
                         vm.eventLoop().autoTickActive();
                     }
 
                     vm.onBeforeExit();
 
-                    vm.handlePendingInternalPromiseRejection();
+                    vm.reportExceptionInHotReloadedModuleIfNeeded();
 
                     vm.eventLoop().tickPossiblyForever();
                 }
diff --git a/src/bun.js/VirtualMachine.zig b/src/bun.js/VirtualMachine.zig
index bb91dc2be00..37c64a40c7e 100644
--- a/src/bun.js/VirtualMachine.zig
+++ b/src/bun.js/VirtualMachine.zig
@@ -677,14 +677,24 @@ pub fn uncaughtException(this: *jsc.VirtualMachine, globalObject: *JSGlobalObjec
     return handled;
 }
 
-pub fn handlePendingInternalPromiseRejection(this: *jsc.VirtualMachine) void {
-    var promise = this.pending_internal_promise.?;
+pub fn reportExceptionInHotReloadedModuleIfNeeded(this: *jsc.VirtualMachine) void {
+    defer this.addMainToWatcherIfNeeded();
+    var promise = this.pending_internal_promise orelse return;
+
     if (promise.status(this.global.vm()) == .rejected and !promise.isHandled(this.global.vm())) {
         this.unhandledRejection(this.global, promise.result(this.global.vm()), promise.asValue());
         promise.setHandled(this.global.vm());
     }
 }
 
+pub fn addMainToWatcherIfNeeded(this: *jsc.VirtualMachine) void {
+    if (this.isWatcherEnabled()) {
+        const main = this.main;
+        if (main.len == 0) return;
+        _ = this.bun_watcher.addFileByPathSlow(main, this.transpiler.options.loader(std.fs.path.extension(main)));
+    }
+}
+
 pub fn defaultOnUnhandledRejection(this: *jsc.VirtualMachine, _: *JSGlobalObject, value: JSValue) void {
     this.runErrorHandler(value, this.onUnhandledRejectionExceptionList);
 }
diff --git a/src/bun.js/hot_reloader.zig b/src/bun.js/hot_reloader.zig
index 90a9b74d305..2f002010035 100644
--- a/src/bun.js/hot_reloader.zig
+++ b/src/bun.js/hot_reloader.zig
@@ -25,6 +25,17 @@ pub const ImportWatcher = union(enum) {
         };
     }
 
+    pub inline fn addFileByPathSlow(
+        this: ImportWatcher,
+        file_path: string,
+        loader: options.Loader,
+    ) bool {
+        return switch (this) {
+            inline .hot, .watch => |w| w.addFileByPathSlow(file_path, loader),
+            else => true,
+        };
+    }
+
     pub inline fn addFile(
         this: ImportWatcher,
         fd: bun.FD,
@@ -63,6 +74,8 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
         verbose: bool = false,
         pending_count: std.atomic.Value(u32) = std.atomic.Value(u32).init(0),
 
+        main: MainFile = .{},
+
         tombstones: bun.StringHashMapUnmanaged(*bun.fs.FileSystem.RealFS.EntriesOption) = .{},
 
         pub fn init(ctx: *Ctx, fs: *bun.fs.FileSystem, verbose: bool, clear_screen_flag: bool) *Watcher {
@@ -105,6 +118,44 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
 
         pub var clear_screen = false;
 
+        const MainFile = struct {
+            /// Includes a trailing "/"
+            dir: []const u8 = "",
+            dir_hash: Watcher.HashType = 0,
+
+            file: []const u8 = "",
+            hash: Watcher.HashType = 0,
+
+            /// On macOS, vim's atomic save triggers a race condition:
+            /// 1. Old file gets NOTE_RENAME (file renamed to temp name: a.js -> a.js~)
+            /// 2. We receive the event and would normally trigger reload immediately
+            /// 3. But the new file hasn't been created yet - reload fails with ENOENT
+            /// 4. New file gets created and written (a.js)
+            /// 5. Parent directory gets NOTE_WRITE
+            ///
+            /// To fix this: when the entrypoint gets NOTE_RENAME, we set this flag
+            /// and skip the reload. Then when the parent directory gets NOTE_WRITE,
+            /// we check if the file exists and trigger the reload.
+            is_waiting_for_dir_change: bool = false,
+
+            pub fn init(file: []const u8) MainFile {
+                var main = MainFile{
+                    .file = file,
+                    .hash = if (file.len > 0) Watcher.getHash(file) else 0,
+                    .is_waiting_for_dir_change = false,
+                };
+
+                if (std.fs.path.dirname(file)) |dir| {
+                    bun.assert(bun.isSliceInBuffer(dir, file));
+                    bun.assert(file.len > dir.len + 1);
+                    main.dir = file[0 .. dir.len + 1];
+                    main.dir_hash = Watcher.getHash(main.dir);
+                }
+
+                return main;
+            }
+        };
+
         pub const Task = struct {
             count: u8 = 0,
             hashes: [8]u32,
@@ -184,7 +235,7 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
             }
         };
 
-        pub fn enableHotModuleReloading(this: *Ctx) void {
+        pub fn enableHotModuleReloading(this: *Ctx, entry_path: ?[]const u8) void {
             if (comptime @TypeOf(this.bun_watcher) == ImportWatcher) {
                 if (this.bun_watcher != .none)
                     return;
@@ -197,6 +248,7 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
             reloader.* = .{
                 .ctx = this,
                 .verbose = Environment.enable_logs or if (@hasField(Ctx, "log")) this.log.level.atLeast(.info) else false,
+                .main = MainFile.init(entry_path orelse ""),
             };
 
             if (comptime @TypeOf(this.bun_watcher) == ImportWatcher) {
@@ -312,7 +364,7 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
 
                 switch (kind) {
                     .file => {
-                        if (event.op.delete or event.op.rename) {
+                        if (event.op.delete or (event.op.rename and Environment.isMac)) {
                             ctx.removeAtIndex(
                                 event.index,
                                 0,
@@ -322,13 +374,29 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
                         }
 
                         if (this.verbose)
-                            debug("File changed: {s}", .{fs.relativeTo(file_path)});
+                            debug("File changed: {s} ({})", .{ fs.relativeTo(file_path), event });
 
                         if (event.op.write or event.op.delete or event.op.rename) {
+                            if (comptime Environment.isMac) {
+                                if (event.op.rename) {
+                                    // Special case for entrypoint: defer reload until we get
+                                    // a directory write event confirming the file exists.
+                                    // This handles vim's save process which renames the old file
+                                    // before the new file is re-created with a different inode.
+                                    if (this.main.hash == current_hash and !reload_immediately) {
+                                        this.main.is_waiting_for_dir_change = true;
+                                        continue;
+                                    }
+                                }
+
+                                // If we got a write event after rename, the file is back - proceed with reload
+                                if (this.main.is_waiting_for_dir_change and this.main.hash == current_hash) {
+                                    this.main.is_waiting_for_dir_change = false;
+                                }
+                            }
+
                             current_task.append(current_hash);
                         }
-
-                        // TODO: delete events?
                     },
                     .directory => {
                         if (comptime Environment.isWindows) {
@@ -350,6 +418,19 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
                                     entries_option = existing;
                                 }
 
+                                if (event.op.write) {
+                                    // Check if the entrypoint now exists after an atomic save.
+                                    // If we previously got a NOTE_RENAME on the entrypoint (vim renamed
+                                    // the file), this directory write event signals that the new
+                                    // file has been re-created. Verify it exists and trigger reload.
+                                    if (this.main.is_waiting_for_dir_change and this.main.dir_hash == current_hash) {
+                                        if (bun.sys.faccessat(file_descriptors[event.index], std.fs.path.basename(this.main.file)) == .result) {
+                                            this.main.is_waiting_for_dir_change = false;
+                                            current_task.append(this.main.hash);
+                                        }
+                                    }
+                                }
+
                                 var affected_i: usize = 0;
 
                                 // if a file descriptor is stale, we need to close it
@@ -397,7 +478,7 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
                                     bun.asByteSlice(changed_name_.?);
                                 if (changed_name.len == 0 or changed_name[0] == '~' or changed_name[0] == '.') continue;
 
-                                const loader = (this.ctx.getLoaders().get(Fs.PathName.init(changed_name).ext) orelse .file);
+                                const loader = (this.ctx.getLoaders().get(Fs.PathName.findExtname(changed_name)) orelse .file);
                                 var prev_entry_id: usize = std.math.maxInt(usize);
                                 if (loader != .file) {
                                     var path_string: bun.PathString = undefined;
@@ -414,6 +495,8 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
                                                     if (file_descriptors[entry_id].isValid()) {
                                                         if (prev_entry_id != entry_id) {
                                                             current_task.append(hashes[entry_id]);
+                                                            if (this.verbose)
+                                                                debug("Removing file: {s}", .{path_string.slice()});
                                                             ctx.removeAtIndex(
                                                                 @as(u16, @truncate(entry_id)),
                                                                 0,
@@ -452,7 +535,7 @@ pub fn NewHotReloader(comptime Ctx: type, comptime EventLoopType: type, comptime
                         }
 
                         if (this.verbose) {
-                            debug("Dir change: {s}", .{fs.relativeTo(file_path)});
+                            debug("Dir change: {s} (affecting {d}, {})", .{ fs.relativeTo(file_path), affected.len, event });
                         }
                     },
                 }
diff --git a/src/bundler/bundle_v2.zig b/src/bundler/bundle_v2.zig
index faaeb043afa..29f2e80497a 100644
--- a/src/bundler/bundle_v2.zig
+++ b/src/bundler/bundle_v2.zig
@@ -935,7 +935,7 @@ pub const BundleV2 = struct {
 
         const pool = try this.allocator().create(ThreadPool);
         if (cli_watch_flag) {
-            Watcher.enableHotModuleReloading(this);
+            Watcher.enableHotModuleReloading(this, null);
         }
         // errdefer pool.destroy();
         errdefer this.graph.heap.deinit();
diff --git a/src/cli/test_command.zig b/src/cli/test_command.zig
index 7d3bf10cbca..23b70343f8e 100644
--- a/src/cli/test_command.zig
+++ b/src/cli/test_command.zig
@@ -1518,8 +1518,8 @@ pub const TestCommand = struct {
             vm.hot_reload = ctx.debug.hot_reload;
 
             switch (vm.hot_reload) {
-                .hot => jsc.hot_reloader.HotReloader.enableHotModuleReloading(vm),
-                .watch => jsc.hot_reloader.WatchReloader.enableHotModuleReloading(vm),
+                .hot => jsc.hot_reloader.HotReloader.enableHotModuleReloading(vm, null),
+                .watch => jsc.hot_reloader.WatchReloader.enableHotModuleReloading(vm, null),
                 else => {},
             }
 
diff --git a/src/fs.zig b/src/fs.zig
index 324ee38e3b1..912cdbcecb4 100644
--- a/src/fs.zig
+++ b/src/fs.zig
@@ -1562,6 +1562,18 @@ pub const PathName = struct {
     ext: string,
     filename: string,
 
+    pub fn findExtname(_path: string) string {
+        var start: usize = 0;
+        if (bun.path.lastIndexOfSep(_path)) |i| {
+            start = i + 1;
+        }
+        const base = _path[start..];
+        if (bun.strings.lastIndexOfChar(base, '.')) |dot| {
+            if (dot > 0) return base[dot..];
+        }
+        return "";
+    }
+
     pub fn extWithoutLeadingDot(self: *const PathName) string {
         return if (self.ext.len > 0 and self.ext[0] == '.') self.ext[1..] else self.ext;
     }
diff --git a/src/sys.zig b/src/sys.zig
index d97d3311a24..c80d767f3aa 100644
--- a/src/sys.zig
+++ b/src/sys.zig
@@ -3182,8 +3182,8 @@ pub fn faccessat(dir_fd: bun.FileDescriptor, subpath: anytype) bun.sys.Maybe(boo
     const has_sentinel = std.meta.sentinel(@TypeOf(subpath)) != null;
 
     if (comptime !has_sentinel) {
-        const path = std.os.toPosixPath(subpath) catch return bun.sys.Maybe(bool){ .err = Error.fromCode(.NAMETOOLONG, .access) };
-        return faccessat(dir_fd, path);
+        const path = std.posix.toPosixPath(subpath) catch return bun.sys.Maybe(bool){ .err = Error.fromCode(.NAMETOOLONG, .access) };
+        return faccessat(dir_fd, &path);
     }
 
     if (comptime Environment.isLinux) {

PATCH

echo "Patch applied successfully."
