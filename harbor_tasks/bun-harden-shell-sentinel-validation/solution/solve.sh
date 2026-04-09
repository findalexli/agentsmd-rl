#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied (check for distinctive line from the patch)
if grep -q 'jsobjs_len: u32 = 0' src/shell/shell.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch using individual sed commands
# This is more reliable than a unified diff patch

echo "Applying patch to shell.zig..."

# 1. Add jsobjs_len field to Lexer struct (after string_refs field)
sed -i '/string_refs: \[\]bun.String,/a\
\
        \/\/ Number of JS object references expected (for bounds validation)\n        jsobjs_len: u32 = 0,' src/shell/shell.zig

# 2. Update new() function signature and initialization
sed -i 's/pub fn new(alloc: Allocator, src: \[\]const u8, strings_to_escape: \[\]bun.String) @This()/pub fn new(alloc: Allocator, src: []const u8, strings_to_escape: []bun.String, jsobjs_len: u32) @This()/g' src/shell/shell.zig
sed -i '/\.string_refs = strings_to_escape,/a\                .jsobjs_len = jsobjs_len,' src/shell/shell.zig

# 3. Update sublexer creation to copy jsobjs_len
sed -i '/\.string_refs = self.string_refs,/a\                .jsobjs_len = self.jsobjs_len,' src/shell/shell.zig

# 4. Fix validateJSObjRefIdx to use jsobjs_len instead of maxInt(u32)
sed -i 's/if (idx >= std.math.maxInt(u32))/if (idx >= self.jsobjs_len)/g' src/shell/shell.zig

# 5. Add SPECIAL_JS_CHAR to SPECIAL_CHARS
sed -i "s/const SPECIAL_CHARS = \[_\]u8{ '\\~', '\['/const SPECIAL_CHARS = [_]u8{ '~', '[', SPECIAL_JS_CHAR/g" src/shell/shell.zig

echo "Applying patch to interpreter.zig..."

# Add jsobjs_len calculation and pass to lexer
sed -i '/const lex_result = brk: {/i\        const jsobjs_len: u32 = @intCast(jsobjs.len);' src/shell/interpreter.zig
sed -i 's/bun.shell.LexerAscii.new(arena_allocator, script, jsstrings_to_escape)/bun.shell.LexerAscii.new(arena_allocator, script, jsstrings_to_escape, jsobjs_len)/g' src/shell/interpreter.zig
sed -i 's/bun.shell.LexerUnicode.new(arena_allocator, script, jsstrings_to_escape)/bun.shell.LexerUnicode.new(arena_allocator, script, jsstrings_to_escape, jsobjs_len)/g' src/shell/interpreter.zig

echo "Applying patch to Builtin.zig..."

# Add bounds check in Builtin.zig
sed -i '/const globalObject = interpreter.event_loop.js.global;/a\
\
                if (file.jsbuf.idx >= interpreter.jsobjs.len) {\n                    globalObject.throw("Invalid JS object reference in shell", .{}) catch {};\n                    return .failed;\n                }\n' src/shell/Builtin.zig

echo "Applying patch to Cmd.zig..."

# Add bounds check in Cmd.zig
sed -i '/const global = this.base.eventLoop().js.global;/a\
\
                if (val.idx >= this.base.interpreter.jsobjs.len) {\n                    return global.throw("Invalid JS object reference in shell", .{});\n                }\n' src/shell/states/Cmd.zig

# Fix stdio array index typos (stdin_no -> stdout_no/stderr_no)
sed -i 's/spawn_args.stdio\[stdin_no\].extractBlob(global, .{ .Blob = blob }, stdout_no)/spawn_args.stdio[stdout_no].extractBlob(global, .{ .Blob = blob }, stdout_no)/g' src/shell/states/Cmd.zig
sed -i 's/spawn_args.stdio\[stdin_no\].extractBlob(global, .{ .Blob = blob }, stderr_no)/spawn_args.stdio[stderr_no].extractBlob(global, .{ .Blob = blob }, stderr_no)/g' src/shell/states/Cmd.zig

# Update TestingAPIs in shell.zig
echo "Applying patch to TestingAPIs in shell.zig..."
sed -i '/var script = std.array_list.Managed(u8).init(arena.allocator());/a\        const jsobjs_len: u32 = @intCast(jsobjs.items.len);' src/shell/shell.zig
sed -i 's/LexerAscii.new(arena.allocator(), script.items\[0..\], jsstrings.items\[0..\])/LexerAscii.new(arena.allocator(), script.items[0..], jsstrings.items[0..], jsobjs_len)/g' src/shell/shell.zig
sed -i 's/LexerUnicode.new(arena.allocator(), script.items\[0..\], jsstrings.items\[0..\])/LexerUnicode.new(arena.allocator(), script.items[0..], jsstrings.items[0..], jsobjs_len)/g' src/shell/shell.zig

echo "Patch applied successfully."
