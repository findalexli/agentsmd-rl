#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

TARGET="src/bundler/barrel_imports.zig"

# Idempotency check: if alias_is_star field already exists, patch is applied
if grep -q 'alias_is_star' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bundler/barrel_imports.zig b/src/bundler/barrel_imports.zig
index 793be16c0a2..53f9de8b918 100644
--- a/src/bundler/barrel_imports.zig
+++ b/src/bundler/barrel_imports.zig
@@ -18,6 +18,9 @@ const BarrelExportResolution = struct {
     import_record_index: u32,
     /// The original alias in the source module (e.g. "d" for `export { d as c }`)
     original_alias: ?[]const u8,
+    /// True when the underlying import is `import * as ns` — propagation
+    /// through this export must treat the target as needing all exports.
+    alias_is_star: bool,
 };

 /// Look up an export name → import_record_index by chasing
@@ -26,7 +29,7 @@ const BarrelExportResolution = struct {
 fn resolveBarrelExport(alias: []const u8, named_exports: JSAst.NamedExports, named_imports: JSAst.NamedImports) ?BarrelExportResolution {
     const export_entry = named_exports.get(alias) orelse return null;
     const import_entry = named_imports.get(export_entry.ref) orelse return null;
-    return .{ .import_record_index = import_entry.import_record_index, .original_alias = import_entry.alias };
+    return .{ .import_record_index = import_entry.import_record_index, .original_alias = import_entry.alias, .alias_is_star = import_entry.alias_is_star };
 }

 /// Analyze a parsed file to determine if it's a barrel and mark unneeded
@@ -483,7 +486,9 @@ pub fn scheduleBarrelDeferredImports(this: *BundleV2, result: *ParseTask.Result.
                 rec = barrel_ir.slice()[resolution.import_record_index];
             }
             if (rec.source_index.isValid()) {
-                try queue.append(queue_alloc, .{ .barrel_source_index = rec.source_index.get(), .alias = propagate_alias, .is_star = false });
+                // When the barrel re-exports a namespace import (`import * as X; export { X }`),
+                // propagate as a star import so the target barrel loads all exports.
+                try queue.append(queue_alloc, .{ .barrel_source_index = rec.source_index.get(), .alias = propagate_alias, .is_star = resolution.alias_is_star });
             }
         }
     }

PATCH

echo "Patch applied successfully."
