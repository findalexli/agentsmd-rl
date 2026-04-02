#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency: check if already fixed (the broken line references component_idx directly)
if ! grep -q 'computeNtFilter(component_idx)' src/glob/GlobWalker.zig 2>/dev/null; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/glob/GlobWalker.zig b/src/glob/GlobWalker.zig
index 5dad5449582..dbd2db63476 100644
--- a/src/glob/GlobWalker.zig
+++ b/src/glob/GlobWalker.zig
@@ -712,7 +712,16 @@ pub fn GlobWalker_(
                 var iterator = Accessor.DirIter.iterate(fd);
                 if (comptime isWindows) {
                     if (@hasDecl(Accessor.DirIter, "setNameFilter")) {
-                        iterator.setNameFilter(this.computeNtFilter(component_idx));
+                        // computeNtFilter operates on a single pattern component.
+                        // When multiple indices are active (e.g. after `**`), the
+                        // kernel filter could hide entries needed by other indices,
+                        // so skip it. The filter is purely an optimization;
+                        // matchPatternImpl still runs for correctness.
+                        const filter: ?[]const u16 = if (active.count() == 1)
+                            this.computeNtFilter(@intCast(active.findFirstSet().?))
+                        else
+                            null;
+                        iterator.setNameFilter(filter);
                     }
                 }
                 this.iter_state.directory.iter = iterator;

PATCH

echo "Patch applied successfully."
