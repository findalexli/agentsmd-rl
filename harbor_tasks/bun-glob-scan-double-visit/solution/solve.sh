#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if ComponentSet alias already exists, patch is applied
if grep -q 'const ComponentSet = bun.bit_set.AutoBitSet' src/glob/GlobWalker.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/collections/bit_set.zig b/src/collections/bit_set.zig
index 78d15107cb7..1565a8842a4 100644
--- a/src/collections/bit_set.zig
+++ b/src/collections/bit_set.zig
@@ -1280,6 +1280,38 @@ pub const AutoBitSet = union(enum) {
         }
     }

+    pub fn count(this: *const AutoBitSet) usize {
+        return switch (this.*) {
+            inline else => |*bitset| bitset.count(),
+        };
+    }
+
+    pub fn findFirstSet(this: *const AutoBitSet) ?usize {
+        return switch (this.*) {
+            inline else => |*bitset| bitset.findFirstSet(),
+        };
+    }
+
+    pub fn iterator(this: *const AutoBitSet, comptime options: IteratorOptions) Iterator(options) {
+        return switch (this.*) {
+            .static => |*s| .{ .static = s.iterator(options) },
+            .dynamic => |*d| .{ .dynamic = d.iterator(options) },
+        };
+    }
+
+    pub fn Iterator(comptime options: IteratorOptions) type {
+        return union(enum) {
+            static: Static.Iterator(options),
+            dynamic: DynamicBitSetUnmanaged.Iterator(options),
+
+            pub fn next(self: *@This()) ?usize {
+                return switch (self.*) {
+                    inline else => |*it| it.next(),
+                };
+            }
+        };
+    }
+
     pub fn deinit(this: *AutoBitSet, allocator: std.mem.Allocator) void {
         switch (std.meta.activeTag(this.*)) {
             .static => {},
diff --git a/src/glob/GlobWalker.zig b/src/glob/GlobWalker.zig
index 2d275a3faab..29aa10ee2dd 100644
--- a/src/glob/GlobWalker.zig
+++ b/src/glob/GlobWalker.zig
@@ -386,6 +386,15 @@ pub fn GlobWalker_(
             }
         }, true);

+        /// Set of active component indices during traversal. At `**/X`
+        /// boundaries the walker needs to both advance past X and keep the
+        /// outer `**` alive; rather than visiting the directory twice, both
+        /// states are tracked in one set and evaluated in a single readdir.
+        ///
+        /// Uses AutoBitSet (inline up to 127 bits, heap-backed beyond) so any
+        /// component count works.
+        const ComponentSet = bun.bit_set.AutoBitSet;
+
         /// The glob walker references the .directory.path so its not safe to
         /// copy/move this
         const IterState = union(enum) {
@@ -415,10 +424,9 @@ pub fn GlobWalker_(
                 path: bun.PathBuffer,
                 dir_path: [:0]const u8,

-                component_idx: u32,
-                pattern: *Component,
-                next_pattern: ?*Component,
-                is_last: bool,
+                /// Active component indices. Multiple indices mean one readdir
+                /// evaluates all of them instead of revisiting the directory.
+                active: ComponentSet,

                 iter_closed: bool = false,
                 at_cwd: bool = false,
@@ -445,7 +453,7 @@ pub fn GlobWalker_(
                         break :is_absolute std.fs.path.isAbsolutePosix(this.walker.pattern);
                     };

-                    if (!is_absolute) break :brk WorkItem.new(this.walker.cwd, 0, .directory);
+                    if (!is_absolute) break :brk WorkItem.new(this.walker.cwd, this.walker.singleSet(0), .directory);

                     was_absolute = true;

@@ -495,7 +503,7 @@ pub fn GlobWalker_(

                     break :brk WorkItem.new(
                         path_without_special_syntax,
-                        starting_component_idx,
+                        this.walker.singleSet(starting_component_idx),
                         .directory,
                     );
                 };
@@ -585,10 +593,7 @@ pub fn GlobWalker_(
                     .iter = undefined,
                     .path = undefined,
                     .dir_path = undefined,
-                    .component_idx = 0,
-                    .pattern = undefined,
-                    .next_pattern = null,
-                    .is_last = false,
+                    .active = undefined,
                     .iter_closed = false,
                     .at_cwd = false,
                 } };
@@ -607,17 +612,23 @@ pub fn GlobWalker_(
                 };

                 var had_dot_dot = false;
-                const component_idx = this.walker.skipSpecialComponents(work_item.idx, &dir_path, &this.iter_state.directory.path, &had_dot_dot);
-
-                // If we've exhausted all pattern components (e.g., pattern was only dots like "../."),
-                // we're done with this work item
-                if (component_idx >= this.walker.patternComponents.items.len) {
-                    if (work_item.fd) |fd| {
-                        this.closeDisallowingCwd(fd);
+                // Single-index sets (the initial WorkItem) may point to Dot/DotBack
+                // or collapsible `**` runs. Multi-index sets only arise mid-traversal
+                // after `**/X` boundaries and are already past any Dots.
+                const active: ComponentSet = set: {
+                    if (work_item.active.count() == 1) {
+                        const single: u32 = @intCast(work_item.active.findFirstSet().?);
+                        const norm = this.walker.skipSpecialComponents(single, &dir_path, &this.iter_state.directory.path, &had_dot_dot);
+                        if (norm >= this.walker.patternComponents.items.len) {
+                            if (work_item.fd) |fd| this.closeDisallowingCwd(fd);
+                            this.iter_state = .get_next;
+                            return .success;
+                        }
+                        break :set this.walker.singleSet(norm);
                     }
-                    this.iter_state = .get_next;
-                    return .success;
-                }
+                    // Multi-index sets are already normalized by evalDir.
+                    break :set work_item.active;
+                };

                 const fd: Accessor.Handle = fd: {
                     if (work_item.fd) |fd| break :fd fd;
@@ -647,59 +658,49 @@ pub fn GlobWalker_(
                     };
                 };

-                // Optimization:
-                // If we have a pattern like:
-                // `packages/*/package.json`
-                //              ^ and we are at this component, with let's say
-                //                a directory named: `packages/frontend/`
-                //
-                // Then we can just open `packages/frontend/package.json` without
-                // doing any iteration on the current directory.
-                //
-                // More generally, we can apply this optimization if we are on the
-                // last component and it is a literal with no special syntax.
-                if (component_idx == this.walker.patternComponents.items.len -| 1 and
-                    this.walker.patternComponents.items[component_idx].syntax_hint == .Literal)
-                {
-                    defer {
-                        this.closeDisallowingCwd(fd);
-                    }
-                    const stackbuf_size = 256;
-                    var stfb = std.heap.stackFallback(stackbuf_size, this.walker.arena.allocator());
-                    const pathz = try stfb.get().dupeZ(u8, this.walker.patternComponents.items[component_idx].patternSlice(this.walker.pattern));
-                    const stat_result: bun.Stat = switch (Accessor.statat(fd, pathz)) {
-                        .err => |e_| {
-                            var e: bun.sys.Error = e_;
-                            if (e.getErrno() == .NOENT) {
+                // Literal-tail optimization: if the only active index is the last
+                // component and it is a Literal, statat() instead of iterating.
+                // Skip for multi-index masks since each index has different needs.
+                if (active.count() == 1) {
+                    const idx: u32 = @intCast(active.findFirstSet().?);
+                    if (idx == this.walker.patternComponents.items.len -| 1 and
+                        this.walker.patternComponents.items[idx].syntax_hint == .Literal)
+                    {
+                        defer this.closeDisallowingCwd(fd);
+                        const stackbuf_size = 256;
+                        var stfb = std.heap.stackFallback(stackbuf_size, this.walker.arena.allocator());
+                        const pathz = try stfb.get().dupeZ(u8, this.walker.patternComponents.items[idx].patternSlice(this.walker.pattern));
+                        const stat_result: bun.Stat = switch (Accessor.statat(fd, pathz)) {
+                            .err => |e_| {
+                                var e: bun.sys.Error = e_;
+                                if (e.getErrno() == .NOENT) {
+                                    this.iter_state = .get_next;
+                                    return .success;
+                                }
+                                return .{ .err = e.withPath(this.walker.patternComponents.items[idx].patternSlice(this.walker.pattern)) };
+                            },
+                            .result => |stat| stat,
+                        };
+                        const matches = (bun.S.ISDIR(@intCast(stat_result.mode)) and !this.walker.only_files) or bun.S.ISREG(@intCast(stat_result.mode)) or !this.walker.only_files;
+                        if (matches) {
+                            if (try this.walker.prepareMatchedPath(pathz, dir_path)) |path| {
+                                this.iter_state = .{ .matched = path };
+                            } else {
                                 this.iter_state = .get_next;
-                                return .success;
                             }
-                            return .{ .err = e.withPath(this.walker.patternComponents.items[component_idx].patternSlice(this.walker.pattern)) };
-                        },
-                        .result => |stat| stat,
-                    };
-                    const matches = (bun.S.ISDIR(@intCast(stat_result.mode)) and !this.walker.only_files) or bun.S.ISREG(@intCast(stat_result.mode)) or !this.walker.only_files;
-                    if (matches) {
-                        if (try this.walker.prepareMatchedPath(pathz, dir_path)) |path| {
-                            this.iter_state = .{ .matched = path };
                         } else {
                             this.iter_state = .get_next;
                         }
-                    } else {
-                        this.iter_state = .get_next;
+                        return .success;
                     }
-                    return .success;
                 }

                 this.iter_state.directory.dir_path = dir_path;
-                this.iter_state.directory.component_idx = component_idx;
-                this.iter_state.directory.pattern = &this.walker.patternComponents.items[component_idx];
-                this.iter_state.directory.next_pattern = if (component_idx + 1 < this.walker.patternComponents.items.len) &this.walker.patternComponents.items[component_idx + 1] else null;
-                this.iter_state.directory.is_last = component_idx == this.walker.patternComponents.items.len - 1;
+                this.iter_state.directory.active = active;
                 this.iter_state.directory.at_cwd = false;
                 this.iter_state.directory.fd = .empty;

-                log("Transition(dirpath={s}, component_idx={d})", .{ dir_path, component_idx });
+                log("Transition(dirpath={s}, active_count={d})", .{ dir_path, active.count() });

                 this.iter_state.directory.fd = fd;
                 const iterator = Accessor.DirIter.iterate(fd);
@@ -736,17 +737,15 @@ pub fn GlobWalker_(
                                     const entry_name = symlink_full_path_z[work_item.entry_start..symlink_full_path_z.len];

                                     var has_dot_dot = false;
-                                    const component_idx = this.walker.skipSpecialComponents(work_item.idx, &symlink_full_path_z, scratch_path_buf, &has_dot_dot);
-
-                                    // If we've exhausted all pattern components, continue to next item
-                                    if (component_idx >= this.walker.patternComponents.items.len) {
-                                        this.iter_state = .get_next;
-                                        continue;
-                                    }
-
-                                    var pattern = this.walker.patternComponents.items[component_idx];
-                                    const next_pattern = if (component_idx + 1 < this.walker.patternComponents.items.len) &this.walker.patternComponents.items[component_idx + 1] else null;
-                                    const is_last = component_idx == this.walker.patternComponents.items.len - 1;
+                                    const active: ComponentSet = if (work_item.active.count() == 1) blk: {
+                                        const single: u32 = @intCast(work_item.active.findFirstSet().?);
+                                        const norm = this.walker.skipSpecialComponents(single, &symlink_full_path_z, scratch_path_buf, &has_dot_dot);
+                                        if (norm >= this.walker.patternComponents.items.len) {
+                                            this.iter_state = .get_next;
+                                            continue;
+                                        }
+                                        break :blk this.walker.singleSet(norm);
+                                    } else work_item.active;

                                     this.iter_state = .get_next;
                                     const maybe_dir_fd: ?Accessor.Handle = switch (try Accessor.openat(this.cwd_fd, symlink_full_path_z)) {
@@ -755,21 +754,8 @@ pub fn GlobWalker_(
                                                 break :brk null;
                                             }
                                             if (this.walker.error_on_broken_symlinks) return .{ .err = this.walker.handleSysErrWithPath(err, symlink_full_path_z) };
-                                            // Broken symlink, but if `only_files` is false we still want to append
-                                            // it to the matched paths
-                                            if (!this.walker.only_files) {
-                                                // (See case A and B in the comment for `matchPatternFile()`)
-                                                // When we encounter a symlink we call the catch all
-                                                // matching function: `matchPatternImpl()` to see if we can avoid following the symlink.
-                                                // So for case A, we just need to check if the pattern is the last pattern.
-                                                if (is_last or
-                                                    (pattern.syntax_hint == .Double and
-                                                        component_idx + 1 == this.walker.patternComponents.items.len -| 1 and
-                                                        next_pattern.?.syntax_hint != .Double and
-                                                        this.walker.matchPatternImpl(next_pattern.?, entry_name)))
-                                                {
-                                                    return .{ .result = try this.walker.prepareMatchedPathSymlink(symlink_full_path_z) orelse continue };
-                                                }
+                                            if (!this.walker.only_files and this.walker.evalFile(active, entry_name)) {
+                                                return .{ .result = try this.walker.prepareMatchedPathSymlink(symlink_full_path_z) orelse continue };
                                             }
                                             continue;
                                         },
@@ -780,43 +766,22 @@ pub fn GlobWalker_(
                                     };

                                     const dir_fd = maybe_dir_fd orelse {
-                                        // No directory file descriptor, it's a file
-                                        if (is_last)
-                                            return .{ .result = try this.walker.prepareMatchedPathSymlink(symlink_full_path_z) orelse continue };
-
-                                        if (pattern.syntax_hint == .Double and
-                                            component_idx + 1 == this.walker.patternComponents.items.len -| 1 and
-                                            next_pattern.?.syntax_hint != .Double and
-                                            this.walker.matchPatternImpl(next_pattern.?, entry_name))
-                                        {
+                                        // Symlink target is a file
+                                        if (this.walker.evalFile(active, entry_name)) {
                                             return .{ .result = try this.walker.prepareMatchedPathSymlink(symlink_full_path_z) orelse continue };
                                         }
-
                                         continue;
                                     };

                                     var add_dir: bool = false;
-                                    // TODO this function calls `matchPatternImpl(pattern,
-                                    // entry_name)` which is redundant because we already called
-                                    // that when we first encountered the symlink
-                                    const recursion_idx_bump_ = this.walker.matchPatternDir(&pattern, next_pattern, entry_name, component_idx, is_last, &add_dir);
-
-                                    if (recursion_idx_bump_) |recursion_idx_bump| {
-                                        if (recursion_idx_bump == 2) {
-                                            try this.walker.workbuf.append(
-                                                this.walker.arena.allocator(),
-                                                WorkItem.newWithFd(work_item.path, component_idx + recursion_idx_bump, .directory, dir_fd),
-                                            );
-                                            try this.walker.workbuf.append(
-                                                this.walker.arena.allocator(),
-                                                WorkItem.newWithFd(work_item.path, component_idx, .directory, dir_fd),
-                                            );
-                                        } else {
-                                            try this.walker.workbuf.append(
-                                                this.walker.arena.allocator(),
-                                                WorkItem.newWithFd(work_item.path, component_idx + recursion_idx_bump, .directory, dir_fd),
-                                            );
-                                        }
+                                    const child = this.walker.evalDir(active, entry_name, &add_dir);
+                                    if (child.count() != 0) {
+                                        try this.walker.workbuf.append(
+                                            this.walker.arena.allocator(),
+                                            WorkItem.newWithFd(work_item.path, child, .directory, dir_fd),
+                                        );
+                                    } else {
+                                        this.closeDisallowingCwd(dir_fd);
                                     }

                                     if (add_dir and !this.walker.only_files) {
@@ -843,13 +808,11 @@ pub fn GlobWalker_(
                             };
                             log("dir: {s} entry: {s}", .{ dir.dir_path, entry.name.slice() });

-                            const dir_iter_state: *const IterState.Directory = &this.iter_state.directory;
-
+                            const active = dir.active;
                             const entry_name = entry.name.slice();
                             switch (entry.kind) {
                                 .file => {
-                                    const matches = this.walker.matchPatternFile(entry_name, dir_iter_state.component_idx, dir.is_last, dir_iter_state.pattern, dir_iter_state.next_pattern);
-                                    if (matches) {
+                                    if (this.walker.evalFile(active, entry_name)) {
                                         const prepared = try this.walker.prepareMatchedPath(entry_name, dir.dir_path) orelse continue;
                                         return .{ .result = prepared };
                                     }
@@ -857,132 +820,83 @@ pub fn GlobWalker_(
                                 },
                                 .directory => {
                                     var add_dir: bool = false;
-                                    const recursion_idx_bump_ = this.walker.matchPatternDir(dir_iter_state.pattern, dir_iter_state.next_pattern, entry_name, dir_iter_state.component_idx, dir_iter_state.is_last, &add_dir);
-
-                                    if (recursion_idx_bump_) |recursion_idx_bump| {
+                                    const child = this.walker.evalDir(active, entry_name, &add_dir);
+                                    if (child.count() != 0) {
                                         const subdir_parts: []const []const u8 = &[_][]const u8{
                                             dir.dir_path[0..dir.dir_path.len],
                                             entry_name,
                                         };
-
                                         const subdir_entry_name = try this.walker.join(subdir_parts);
-
-                                        if (recursion_idx_bump == 2) {
-                                            try this.walker.workbuf.append(
-                                                this.walker.arena.allocator(),
-                                                WorkItem.new(subdir_entry_name, dir_iter_state.component_idx + recursion_idx_bump, .directory),
-                                            );
-                                            try this.walker.workbuf.append(
-                                                this.walker.arena.allocator(),
-                                                WorkItem.new(subdir_entry_name, dir_iter_state.component_idx, .directory),
-                                            );
-                                        } else {
-                                            try this.walker.workbuf.append(
-                                                this.walker.arena.allocator(),
-                                                WorkItem.new(subdir_entry_name, dir_iter_state.component_idx + recursion_idx_bump, .directory),
-                                            );
-                                        }
+                                        try this.walker.workbuf.append(
+                                            this.walker.arena.allocator(),
+                                            WorkItem.new(subdir_entry_name, child, .directory),
+                                        );
                                     }
-
                                     if (add_dir and !this.walker.only_files) {
                                         const prepared_path = try this.walker.prepareMatchedPath(entry_name, dir.dir_path) orelse continue;
                                         return .{ .result = prepared_path };
                                     }
-
                                     continue;
                                 },
                                 .sym_link => {
                                     if (this.walker.follow_symlinks) {
-                                        // Following a symlink requires additional syscalls, so
-                                        // we first try it against our "catch-all" pattern match
-                                        // function
-                                        const matches = this.walker.matchPatternImpl(dir_iter_state.pattern, entry_name);
-                                        if (!matches) continue;
+                                        if (!this.walker.evalImpl(active, entry_name)) continue;

                                         const subdir_parts: []const []const u8 = &[_][]const u8{
                                             dir.dir_path[0..dir.dir_path.len],
                                             entry_name,
                                         };
                                         const entry_start: u32 = @intCast(if (dir.dir_path.len == 0) 0 else dir.dir_path.len + 1);
-
-                                        // const subdir_entry_name = try this.arena.allocator().dupe(u8, ResolvePath.join(subdir_parts, .auto));
                                         const subdir_entry_name = try this.walker.join(subdir_parts);

                                         try this.walker.workbuf.append(
                                             this.walker.arena.allocator(),
-                                            WorkItem.newSymlink(subdir_entry_name, dir_iter_state.component_idx, entry_start),
+                                            WorkItem.newSymlink(subdir_entry_name, active, entry_start),
                                         );
-
                                         continue;
                                     }

                                     if (this.walker.only_files) continue;

-                                    const matches = this.walker.matchPatternFile(entry_name, dir_iter_state.component_idx, dir_iter_state.is_last, dir_iter_state.pattern, dir_iter_state.next_pattern);
-                                    if (matches) {
+                                    if (this.walker.evalFile(active, entry_name)) {
                                         const prepared_path = try this.walker.prepareMatchedPath(entry_name, dir.dir_path) orelse continue;
                                         return .{ .result = prepared_path };
                                     }
-
                                     continue;
                                 },
-                                // Some filesystems (e.g., Docker bind mounts, FUSE, NFS) return
-                                // DT_UNKNOWN for d_type. Use lazy stat to determine the real kind
-                                // only when needed (PR #18172 pattern for performance).
                                 .unknown => {
-                                    // First check if name might match pattern (avoid unnecessary stat)
-                                    const might_match = this.walker.matchPatternImpl(dir_iter_state.pattern, entry_name);
-                                    if (!might_match) continue;
+                                    if (!this.walker.evalImpl(active, entry_name)) continue;

-                                    // Need to stat to determine actual kind (lstatat to not follow symlinks)
-                                    // Use stack fallback for short names (typical case) to avoid arena allocation
                                     const stackbuf_size = 256;
                                     var stfb = std.heap.stackFallback(stackbuf_size, this.walker.arena.allocator());
                                     const name_z = bun.handleOom(stfb.get().dupeZ(u8, entry_name));
                                     const stat_result = Accessor.lstatat(dir.fd, name_z);
                                     const real_kind = switch (stat_result) {
                                         .result => |st| bun.sys.kindFromMode(@intCast(st.mode)),
-                                        .err => continue, // Skip entries we can't stat
+                                        .err => continue,
                                     };

-                                    // Process based on actual kind
                                     switch (real_kind) {
                                         .file => {
-                                            const matches = this.walker.matchPatternFile(entry_name, dir_iter_state.component_idx, dir.is_last, dir_iter_state.pattern, dir_iter_state.next_pattern);
-                                            if (matches) {
+                                            if (this.walker.evalFile(active, entry_name)) {
                                                 const prepared = try this.walker.prepareMatchedPath(entry_name, dir.dir_path) orelse continue;
                                                 return .{ .result = prepared };
                                             }
                                         },
                                         .directory => {
                                             var add_dir: bool = false;
-                                            const recursion_idx_bump_ = this.walker.matchPatternDir(dir_iter_state.pattern, dir_iter_state.next_pattern, entry_name, dir_iter_state.component_idx, dir_iter_state.is_last, &add_dir);
-
-                                            if (recursion_idx_bump_) |recursion_idx_bump| {
+                                            const child = this.walker.evalDir(active, entry_name, &add_dir);
+                                            if (child.count() != 0) {
                                                 const subdir_parts: []const []const u8 = &[_][]const u8{
                                                     dir.dir_path[0..dir.dir_path.len],
                                                     entry_name,
                                                 };
-
                                                 const subdir_entry_name = try this.walker.join(subdir_parts);
-
-                                                if (recursion_idx_bump == 2) {
-                                                    try this.walker.workbuf.append(
-                                                        this.walker.arena.allocator(),
-                                                        WorkItem.new(subdir_entry_name, dir_iter_state.component_idx + recursion_idx_bump, .directory),
-                                                    );
-                                                    try this.walker.workbuf.append(
-                                                        this.walker.arena.allocator(),
-                                                        WorkItem.new(subdir_entry_name, dir_iter_state.component_idx, .directory),
-                                                    );
-                                                } else {
-                                                    try this.walker.workbuf.append(
-                                                        this.walker.arena.allocator(),
-                                                        WorkItem.new(subdir_entry_name, dir_iter_state.component_idx + recursion_idx_bump, .directory),
-                                                    );
-                                                }
+                                                try this.walker.workbuf.append(
+                                                    this.walker.arena.allocator(),
+                                                    WorkItem.new(subdir_entry_name, child, .directory),
+                                                );
                                             }
-
                                             if (add_dir and !this.walker.only_files) {
                                                 const prepared_path = try this.walker.prepareMatchedPath(entry_name, dir.dir_path) orelse continue;
                                                 return .{ .result = prepared_path };
@@ -996,20 +910,18 @@ pub fn GlobWalker_(
                                                 };
                                                 const entry_start: u32 = @intCast(if (dir.dir_path.len == 0) 0 else dir.dir_path.len + 1);
                                                 const subdir_entry_name = try this.walker.join(subdir_parts);
-
                                                 try this.walker.workbuf.append(
                                                     this.walker.arena.allocator(),
-                                                    WorkItem.newSymlink(subdir_entry_name, dir_iter_state.component_idx, entry_start),
+                                                    WorkItem.newSymlink(subdir_entry_name, active, entry_start),
                                                 );
                                             } else if (!this.walker.only_files) {
-                                                const matches = this.walker.matchPatternFile(entry_name, dir_iter_state.component_idx, dir_iter_state.is_last, dir_iter_state.pattern, dir_iter_state.next_pattern);
-                                                if (matches) {
+                                                if (this.walker.evalFile(active, entry_name)) {
                                                     const prepared_path = try this.walker.prepareMatchedPath(entry_name, dir.dir_path) orelse continue;
                                                     return .{ .result = prepared_path };
                                                 }
                                             }
                                         },
-                                        else => {}, // Skip other types (block devices, etc.)
+                                        else => {},
                                     }
                                     continue;
                                 },
@@ -1023,7 +935,8 @@ pub fn GlobWalker_(

         const WorkItem = struct {
             path: []const u8,
-            idx: u32,
+            /// Bitmask of active component indices.
+            active: ComponentSet,
             kind: Kind,
             entry_start: u32 = 0,
             fd: ?Accessor.Handle = null,
@@ -1033,30 +946,16 @@ pub fn GlobWalker_(
                 symlink,
             };

-            fn new(path: []const u8, idx: u32, kind: Kind) WorkItem {
-                return .{
-                    .path = path,
-                    .idx = idx,
-                    .kind = kind,
-                };
+            fn new(path: []const u8, active: ComponentSet, kind: Kind) WorkItem {
+                return .{ .path = path, .active = active, .kind = kind };
             }

-            fn newWithFd(path: []const u8, idx: u32, kind: Kind, fd: Accessor.Handle) WorkItem {
-                return .{
-                    .path = path,
-                    .idx = idx,
-                    .kind = kind,
-                    .fd = fd,
-                };
+            fn newWithFd(path: []const u8, active: ComponentSet, kind: Kind, fd: Accessor.Handle) WorkItem {
+                return .{ .path = path, .active = active, .kind = kind, .fd = fd };
             }

-            fn newSymlink(path: []const u8, idx: u32, entry_start: u32) WorkItem {
-                return .{
-                    .path = path,
-                    .idx = idx,
-                    .kind = .symlink,
-                    .entry_start = entry_start,
-                };
+            fn newSymlink(path: []const u8, active: ComponentSet, entry_start: u32) WorkItem {
+                return .{ .path = path, .active = active, .kind = .symlink, .entry_start = entry_start };
             }
         };

@@ -1439,6 +1338,78 @@ pub fn GlobWalker_(
             ).matches();
         }

+        /// Create an empty ComponentSet sized for this pattern.
+        fn makeSet(this: *GlobWalker) ComponentSet {
+            return bun.handleOom(ComponentSet.initEmpty(
+                this.arena.allocator(),
+                this.patternComponents.items.len,
+            ));
+        }
+
+        fn singleSet(this: *GlobWalker, idx: u32) ComponentSet {
+            var s = this.makeSet();
+            s.set(idx);
+            return s;
+        }
+
+        /// Evaluate a directory entry against all active component indices.
+        /// Returns the child's active set (union of all recursion targets).
+        /// Sets `add` if any index says the directory itself is a match.
+        fn evalDir(this: *GlobWalker, active: ComponentSet, entry_name: []const u8, add: *bool) ComponentSet {
+            var child = this.makeSet();
+            const comps = this.patternComponents.items;
+            const len: u32 = @intCast(comps.len);
+            var it = active.iterator(.{});
+            while (it.next()) |i| {
+                const idx: u32 = @intCast(i);
+                const pattern = &comps[idx];
+                const next_pattern = if (idx + 1 < len) &comps[idx + 1] else null;
+                const is_last = idx == len - 1;
+                var add_this = false;
+                if (this.matchPatternDir(pattern, next_pattern, entry_name, idx, is_last, &add_this)) |bump| {
+                    child.set(this.normalizeIdx(idx + bump));
+                    // At `**/X` boundaries, keep the outer `**` alive unless
+                    // idx+2 is itself `**` (whose recursion already covers it).
+                    if (bump == 2 and comps[idx + 2].syntax_hint != .Double) {
+                        child.set(idx);
+                    }
+                }
+                if (add_this) add.* = true;
+            }
+            return child;
+        }
+
+        fn evalFile(this: *GlobWalker, active: ComponentSet, entry_name: []const u8) bool {
+            const comps = this.patternComponents.items;
+            const len: u32 = @intCast(comps.len);
+            var it = active.iterator(.{});
+            while (it.next()) |i| {
+                const idx: u32 = @intCast(i);
+                const pattern = &comps[idx];
+                const next_pattern = if (idx + 1 < len) &comps[idx + 1] else null;
+                const is_last = idx == len - 1;
+                if (this.matchPatternFile(entry_name, idx, is_last, pattern, next_pattern)) return true;
+            }
+            return false;
+        }
+
+        fn evalImpl(this: *GlobWalker, active: ComponentSet, entry_name: []const u8) bool {
+            var it = active.iterator(.{});
+            while (it.next()) |idx| {
+                if (this.matchPatternImpl(&this.patternComponents.items[idx], entry_name)) return true;
+            }
+            return false;
+        }
+
+        inline fn normalizeIdx(this: *const GlobWalker, idx: u32) u32 {
+            if (idx < this.patternComponents.items.len and
+                this.patternComponents.items[idx].syntax_hint == .Double)
+            {
+                return @constCast(this).collapseSuccessiveDoubleWildcards(idx);
+            }
+            return idx;
+        }
+
         inline fn matchedPathToBunString(matched_path: MatchedPath) BunString {
             if (comptime sentinel) {
                 return BunString.fromBytes(matched_path[0 .. matched_path.len + 1]);
diff --git a/test/js/bun/glob/scan.test.ts b/test/js/bun/glob/scan.test.ts
index 54b23bda26c..2975ff2aa5d 100644
--- a/test/js/bun/glob/scan.test.ts
+++ b/test/js/bun/glob/scan.test.ts
@@ -814,3 +814,36 @@ describe("glob.scan wildcard fast path", async () => {
     );
   });
 });
+
+// ComponentSet (AutoBitSet) stores up to 127 indices inline, then spills to
+// heap. Verify patterns past that threshold still match correctly.
+// Skipped on Windows: 130 levels × 2 chars + tmpdir prefix exceeds MAX_PATH (260).
+test.skipIf(process.platform === "win32")("patterns with many components", () => {
+  const depth = 130;
+  const files: Record<string, string> = {};
+  const parts: string[] = [];
+  for (let i = 0; i < depth; i++) parts.push("a");
+  files[parts.join("/") + "/hit.txt"] = "";
+  files[parts.slice(0, depth - 1).join("/") + "/miss.txt"] = "";
+
+  const dir = tempDirWithFiles("glob-deep", files);
+
+  // Exact-depth pattern: depth `*` components + literal tail
+  const star = Array(depth).fill("*").join("/") + "/hit.txt";
+  expect([...new Bun.Glob(star).scanSync({ cwd: dir })].length).toBe(1);
+
+  // `**` at the start with a deep literal prefix after it
+  const deepDouble = "**/" + Array(depth).fill("a").join("/") + "/*.txt";
+  expect([...new Bun.Glob(deepDouble).scanSync({ cwd: dir })].length).toBe(1);
+
+  // `**` sandwiched deep in the pattern (triggers merge at high index)
+  const half = Math.floor(depth / 2);
+  const sandwich =
+    Array(half).fill("*").join("/") +
+    "/**/" +
+    Array(depth - half)
+      .fill("a")
+      .join("/") +
+    "/*.txt";
+  expect([...new Bun.Glob(sandwich).scanSync({ cwd: dir })].length).toBe(1);
+});

PATCH
