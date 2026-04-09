#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied (check for the early return we add)
if grep -q 'if (self.tokens.items.len == 0) return;' src/shell/braces.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
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
diff --git a/test/js/bun/shell/brace.test.ts b/test/js/bun/shell/brace.test.ts
index 44601fa0c9f..99532b2b759 100644
--- a/test/js/bun/shell/brace.test.ts
+++ b/test/js/bun/shell/brace.test.ts
@@ -50,6 +50,12 @@ describe("$.braces", () => {
     ]);
   });

+  test("empty string", () => {
+    expect($.braces("")).toEqual([""]);
+    expect($.braces("", { parse: true })).toBeString();
+    expect($.braces("", { tokenize: true })).toBeString();
+  });
+
   test("unicode", () => {
     const result = $.braces(`lol {😂,🫵,🤣}`);
     expect(result).toEqual(["lol 😂", "lol 🫵", "lol 🤣"]);
PATCH

echo "Patch applied successfully."
