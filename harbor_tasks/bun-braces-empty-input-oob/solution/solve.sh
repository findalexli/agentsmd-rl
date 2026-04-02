#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line from the fix)
if grep -q 'if (self.tokens.items.len == 0) return;' src/shell/braces.zig; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/shell/braces.zig b/src/shell/braces.zig
index 3f9ef5cf6c9..ab0a2597765 100644
--- a/src/shell/braces.zig
+++ b/src/shell/braces.zig
@@ -307,7 +307,7 @@ pub const Parser = struct {
         if (!self.is_at_end()) {
             self.current += 1;
         }
-        return self.prev();
+        return if (self.current > 0) self.prev() else self.peek();
     }

     fn is_at_end(self: *Parser) bool {
@@ -588,6 +588,7 @@ pub fn NewLexer(comptime encoding: Encoding) type {
         }

         fn flattenTokens(self: *@This()) Allocator.Error!void {
+            if (self.tokens.items.len == 0) return;
             var brace_count: u32 = if (self.tokens.items[0] == .open) 1 else 0;
             var i: u32 = 0;
             var j: u32 = 1;

PATCH
