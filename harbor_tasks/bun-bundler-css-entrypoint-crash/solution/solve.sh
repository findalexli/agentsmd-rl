#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

TARGET="src/bundler/linker_context/computeChunks.zig"

# Idempotency check: if the mapping array already exists, patch is applied
if grep -q 'entry_point_to_js_chunk_idx' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bundler/linker_context/computeChunks.zig b/src/bundler/linker_context/computeChunks.zig
index db9e9cb3153..0dbb9ab7d88 100644
--- a/src/bundler/linker_context/computeChunks.zig
+++ b/src/bundler/linker_context/computeChunks.zig
@@ -20,6 +20,11 @@ pub noinline fn computeChunks(
     var css_chunks = std.AutoArrayHashMap(u64, Chunk).init(temp_allocator);
     var js_chunks_with_css: usize = 0;

+    // Maps entry point IDs to their index in js_chunks.values().
+    // CSS-only entry points that skip JS chunk creation get maxInt as sentinel.
+    const entry_point_to_js_chunk_idx = try temp_allocator.alloc(u32, this.graph.entry_points.len);
+    @memset(entry_point_to_js_chunk_idx, std.math.maxInt(u32));
+
     const entry_source_indices = this.graph.entry_points.items(.source_index);
     const css_asts = this.graph.ast.items(.css);
     var html_chunks = bun.StringArrayHashMap(Chunk).init(temp_allocator);
@@ -119,6 +124,7 @@ pub noinline fn computeChunks(
         // Create a chunk for the entry point here to ensure that the chunk is
         // always generated even if the resulting file is empty
         const js_chunk_entry = try js_chunks.getOrPut(js_chunk_key);
+        entry_point_to_js_chunk_idx[entry_id_] = @intCast(js_chunk_entry.index);
         js_chunk_entry.value_ptr.* = .{
             .entry_point = .{
                 .entry_point_id = entry_bit,
@@ -202,9 +208,15 @@ pub noinline fn computeChunks(
         chunks: []Chunk,
         allocator: std.mem.Allocator,
         source_id: u32,
+        entry_point_to_js_chunk_idx: []const u32,
+
+        pub fn next(c: *@This(), entry_point_id: usize) void {
+            // Map the entry point ID to the actual JS chunk index.
+            // CSS-only entry points don't have JS chunks (sentinel value).
+            const chunk_idx = c.entry_point_to_js_chunk_idx[entry_point_id];
+            if (chunk_idx == std.math.maxInt(u32)) return;

-        pub fn next(c: *@This(), chunk_id: usize) void {
-            const entry = c.chunks[chunk_id].files_with_parts_in_chunk.getOrPut(c.allocator, @as(u32, @truncate(c.source_id))) catch unreachable;
+            const entry = c.chunks[chunk_idx].files_with_parts_in_chunk.getOrPut(c.allocator, @as(u32, @truncate(c.source_id))) catch unreachable;
             if (!entry.found_existing) {
                 entry.value_ptr.* = 0; // Initialize byte count to 0
             }
@@ -259,6 +271,7 @@ pub noinline fn computeChunks(
                             .chunks = js_chunks.values(),
                             .allocator = this.allocator(),
                             .source_id = source_index.get(),
+                            .entry_point_to_js_chunk_idx = entry_point_to_js_chunk_idx,
                         };
                         entry_bits.forEach(Handler, &handler, Handler.next);
                     }

PATCH

echo "Patch applied successfully."
