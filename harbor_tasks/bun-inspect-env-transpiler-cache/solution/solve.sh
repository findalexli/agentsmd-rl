#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (the fix adds RuntimeTranspilerCache.is_disabled inside configureDebugger)
if grep -q 'RuntimeTranspilerCache.is_disabled = true' src/bun.js/VirtualMachine.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/VirtualMachine.zig b/src/bun.js/VirtualMachine.zig
index a9945bebf99..d862e935a4f 100644
--- a/src/bun.js/VirtualMachine.zig
+++ b/src/bun.js/VirtualMachine.zig
@@ -1271,11 +1271,18 @@ fn configureDebugger(this: *VirtualMachine, cli_flag: bun.cli.Command.Debugger)
         },
     }

-    if (this.isInspectorEnabled() and this.debugger.?.mode != .connect) {
-        this.transpiler.options.minify_identifiers = false;
-        this.transpiler.options.minify_syntax = false;
-        this.transpiler.options.minify_whitespace = false;
-        this.transpiler.options.debugger = true;
+    if (this.isInspectorEnabled()) {
+        // The runtime transpiler cache does not store inline source maps needed
+        // by the debugger frontend. Disable it so the printer always runs and
+        // generates the inline sourceMappingURL for the inspector.
+        jsc.RuntimeTranspilerCache.is_disabled = true;
+
+        if (this.debugger.?.mode != .connect) {
+            this.transpiler.options.minify_identifiers = false;
+            this.transpiler.options.minify_syntax = false;
+            this.transpiler.options.minify_whitespace = false;
+            this.transpiler.options.debugger = true;
+        }
     }
 }

diff --git a/src/cli/Arguments.zig b/src/cli/Arguments.zig
index f1406babc96..f2c22e5a202 100644
--- a/src/cli/Arguments.zig
+++ b/src/cli/Arguments.zig
@@ -838,8 +838,6 @@ pub fn parse(allocator: std.mem.Allocator, ctx: Command.Context, comptime cmd: C
                 Command.Debugger{ .enable = .{
                     .path_or_port = inspect_flag,
                 } };
-
-            bun.jsc.RuntimeTranspilerCache.is_disabled = true;
         } else if (args.option("--inspect-wait")) |inspect_flag| {
             ctx.runtime_options.debugger = if (inspect_flag.len == 0)
                 Command.Debugger{ .enable = .{
@@ -850,8 +848,6 @@ pub fn parse(allocator: std.mem.Allocator, ctx: Command.Context, comptime cmd: C
                     .path_or_port = inspect_flag,
                     .wait_for_connection = true,
                 } };
-
-            bun.jsc.RuntimeTranspilerCache.is_disabled = true;
         } else if (args.option("--inspect-brk")) |inspect_flag| {
             ctx.runtime_options.debugger = if (inspect_flag.len == 0)
                 Command.Debugger{ .enable = .{
@@ -864,8 +860,6 @@ pub fn parse(allocator: std.mem.Allocator, ctx: Command.Context, comptime cmd: C
                     .wait_for_connection = true,
                     .set_breakpoint_on_first_line = true,
                 } };
-
-            bun.jsc.RuntimeTranspilerCache.is_disabled = true;
         }

         const cpu_prof_flag = args.flag("--cpu-prof");

PATCH

echo "Patch applied successfully."
