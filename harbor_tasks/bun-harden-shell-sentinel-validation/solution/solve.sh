#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied (check for distinctive line from the patch)
if grep -q 'jsobjs_len: u32 = 0' src/shell/shell.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/shell/Builtin.zig b/src/shell/Builtin.zig
index b29ff240094..dc6c2cc9604 100644
--- a/src/shell/Builtin.zig
+++ b/src/shell/Builtin.zig
@@ -510,6 +510,12 @@ fn initRedirections(
             },
             .jsbuf => |val| {
                 const globalObject = interpreter.event_loop.js.global;
+
+                if (file.jsbuf.idx >= interpreter.jsobjs.len) {
+                    globalObject.throw("Invalid JS object reference in shell", .{}) catch {};
+                    return .failed;
+                }
+
                 if (interpreter.jsobjs[file.jsbuf.idx].asArrayBuffer(globalObject)) |buf| {
                     const arraybuf: BuiltinIO.ArrayBuf = .{ .buf = jsc.ArrayBuffer.Strong{
                         .array_buffer = buf,
diff --git a/src/shell/interpreter.zig b/src/shell/interpreter.zig
index 7ca6c2bf413..95c0526ffb4 100644
--- a/src/shell/interpreter.zig
+++ b/src/shell/interpreter.zig
@@ -792,13 +792,14 @@ pub const Interpreter = struct {
         out_parser: *?bun.shell.Parser,
         out_lex_result: *?shell.LexResult,
     ) !ast.Script {
+        const jsobjs_len: u32 = @intCast(jsobjs.len);
         const lex_result = brk: {
             if (bun.strings.isAllASCII(script)) {
-                var lexer = bun.shell.LexerAscii.new(arena_allocator, script, jsstrings_to_escape);
+                var lexer = bun.shell.LexerAscii.new(arena_allocator, script, jsstrings_to_escape, jsobjs_len);
                 try lexer.lex();
                 break :brk lexer.get_result();
             }
-            var lexer = bun.shell.LexerUnicode.new(arena_allocator, script, jsstrings_to_escape);
+            var lexer = bun.shell.LexerUnicode.new(arena_allocator, script, jsstrings_to_escape, jsobjs_len);
             try lexer.lex();
             break :brk lexer.get_result();
         };
diff --git a/src/shell/shell.zig b/src/shell/shell.zig
index 6a5174cb356..2111db8b651 100644
--- a/src/shell/shell.zig
+++ b/src/shell/shell.zig
@@ -2334,6 +2334,9 @@ pub fn NewLexer(comptime encoding: StringEncoding) type {
         /// Not owned by this struct
         string_refs: []bun.String,

+        /// Number of JS object references expected (for bounds validation)
+        jsobjs_len: u32 = 0,
+
         const SubShellKind = enum {
             /// (echo hi; echo hello)
             normal,
@@ -2363,13 +2366,14 @@ pub fn NewLexer(comptime encoding: StringEncoding) type {
             delimit_quote: bool,
         };

-        pub fn new(alloc: Allocator, src: []const u8, strings_to_escape: []bun.String) @This() {
+        pub fn new(alloc: Allocator, src: []const u8, strings_to_escape: []bun.String, jsobjs_len: u32) @This() {
             return .{
                 .chars = Chars.init(src),
                 .tokens = ArrayList(Token).init(alloc),
                 .strpool = ArrayList(u8).init(alloc),
                 .errors = ArrayList(LexError).init(alloc),
                 .string_refs = strings_to_escape,
+                .jsobjs_len = jsobjs_len,
             };
         }

@@ -2400,6 +2404,7 @@ pub fn NewLexer(comptime encoding: StringEncoding) type {
                 .word_start = self.word_start,
                 .j = self.j,
                 .string_refs = self.string_refs,
+                .jsobjs_len = self.jsobjs_len,
             };
             sublexer.chars.state = .Normal;
             return sublexer;
@@ -3358,7 +3363,7 @@ pub fn NewLexer(comptime encoding: StringEncoding) type {
         }

         fn validateJSObjRefIdx(self: *@This(), idx: usize) bool {
-            if (idx >= std.math.maxInt(u32)) {
+            if (idx >= self.jsobjs_len) {
                 self.add_error("Invalid JS object ref (out of bounds)");
                 return false;
             }
@@ -4129,7 +4134,7 @@ pub const ShellSrcBuilder = struct {
 };

 /// Characters that need to escaped
-const SPECIAL_CHARS = [_]u8{ '~', '[', ']', '#', ';', '\n', '*', '{', ',', '}', '`', '$', '=', '(', ')', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '|', '>', '<', '&', '\'', '"', ' ', '\\' };
+const SPECIAL_CHARS = [_]u8{ '~', '[', ']', '#', ';', '\n', '*', '{', ',', '}', '`', '$', '=', '(', ')', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '|', '>', '<', '&', '\'', '"', ' ', '\\', SPECIAL_JS_CHAR };
 const SPECIAL_CHARS_TABLE: bun.bit_set.IntegerBitSet(256) = brk: {
     var table = bun.bit_set.IntegerBitSet(256).initEmpty();
     for (SPECIAL_CHARS) |c| {
@@ -4554,15 +4559,16 @@ pub const TestingAPIs = struct {
         var script = std.array_list.Managed(u8).init(arena.allocator());
         try shellCmdFromJS(globalThis, string_args, &template_args, &jsobjs, &jsstrings, &script, marked_argument_buffer);

+        const jsobjs_len: u32 = @intCast(jsobjs.items.len);
         const lex_result = brk: {
             if (bun.strings.isAllASCII(script.items[0..])) {
-                var lexer = LexerAscii.new(arena.allocator(), script.items[0..], jsstrings.items[0..]);
+                var lexer = LexerAscii.new(arena.allocator(), script.items[0..], jsstrings.items[0..], jsobjs_len);
                 lexer.lex() catch |err| {
                     return globalThis.throwError(err, "failed to lex shell");
                 };
                 break :brk lexer.get_result();
             }
-            var lexer = LexerUnicode.new(arena.allocator(), script.items[0..], jsstrings.items[0..]);
+            var lexer = LexerUnicode.new(arena.allocator(), script.items[0..], jsstrings.items[0..], jsobjs_len);
             lexer.lex() catch |err| {
                 return globalThis.throwError(err, "failed to lex shell");
             };
diff --git a/src/shell/states/Cmd.zig b/src/shell/states/Cmd.zig
index 125c297262a..0128ef2dc2f 100644
--- a/src/shell/states/Cmd.zig
+++ b/src/shell/states/Cmd.zig
@@ -556,6 +556,10 @@ fn initRedirections(this: *Cmd, spawn_args: *Subprocess.SpawnArgs) bun.JSError!?
                 if (this.base.eventLoop() != .js) @panic("JS values not allowed in this context");
                 const global = this.base.eventLoop().js.global;

+                if (val.idx >= this.base.interpreter.jsobjs.len) {
+                    return global.throw("Invalid JS object reference in shell", .{});
+                }
+
                 if (this.base.interpreter.jsobjs[val.idx].asArrayBuffer(global)) |buf| {
                     const stdio: bun.shell.subproc.Stdio = .{ .array_buffer = jsc.ArrayBuffer.Strong{
                         .array_buffer = buf,
@@ -568,9 +572,9 @@ fn initRedirections(this: *Cmd, spawn_args: *Subprocess.SpawnArgs) bun.JSError!?                 if (this.node.redirect.stdin) {
                     try spawn_args.stdio[stdin_no].extractBlob(global, .{ .Blob = blob }, stdin_no);
                 } else if (this.node.redirect.stdout) {
-                    try spawn_args.stdio[stdin_no].extractBlob(global, .{ .Blob = blob }, stdout_no);
+                    try spawn_args.stdio[stdout_no].extractBlob(global, .{ .Blob = blob }, stdout_no);
                 } else if (this.node.redirect.stderr) {
-                    try spawn_args.stdio[stdin_no].extractBlob(global, .{ .Blob = blob }, stderr_no);
+                    try spawn_args.stdio[stderr_no].extractBlob(global, .{ .Blob = blob }, stderr_no);
                 }
                 } else if (try jsc.WebCore.ReadableStream.fromJS(this.base.interpreter.jsobjs[val.idx], global)) |rstream| {
                     _ = rstream;
PATCH

echo "Patch applied successfully."
