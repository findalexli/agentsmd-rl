# Harden Shell Interpolation and Object Reference Validation

## Problem

Bun's shell implementation uses an internal sentinel byte (`\x08`) to mark JavaScript object and string references in shell command templates. When user-supplied strings containing this sentinel byte are passed to shell commands, the current implementation fails to properly escape them, leading to:

1. **Lex errors**: Strings containing `\x08__bun_` or `\x08__bunstr_` prefixes are misinterpreted as malformed internal object references, causing the shell lexer to fail.

2. **Potential out-of-bounds access**: When `\x08__bun_NNNN` patterns (where NNNN is a number) are injected via `{ raw: ... }`, the `validateJSObjRefIdx` function only checked if the index exceeded `maxInt(u32)` rather than the actual array length. This could lead to accessing `jsobjs[9999]` on an empty array.

3. **Incorrect stdio indices**: The redirection code in `Cmd.zig` incorrectly used `stdin_no` when extracting blobs for stdout and stderr redirects.

## Symptoms

- Passing strings with the byte sequence `\x08__bun_abc` to shell interpolation causes lex errors
- Using `{ raw: sentinel_pattern }` with out-of-bounds indices could cause crashes
- Shell commands with certain string arguments fail unexpectedly

## Expected Behavior

- All user-supplied strings, including those containing the internal sentinel byte, should round-trip through shell interpolation correctly
- Out-of-bounds object references should be caught early and throw a proper JavaScript error: `"Invalid JS object reference in shell"`
- Stdio redirections should use the correct file descriptor indices

## Files to Look At

- `src/shell/shell.zig` — The shell lexer and `SPECIAL_CHARS` table. Look for `validateJSObjRefIdx` and the `NewLexer` struct.

- `src/shell/interpreter.zig` — Shell interpreter that creates lexers. Check how `LexerAscii` and `LexerUnicode` are instantiated.

- `src/shell/states/Cmd.zig` — Command state handling redirections. Look for `initRedirections` function.

- `src/shell/Builtin.zig` — Builtin command handling. Look for redirection handling in builtin commands.

## Key Technical Details

- The sentinel byte is `0x08` (backspace character), defined as `SPECIAL_JS_CHAR` in the shell code
- The internal reference patterns are `\x08__bun_NNNN` for objects and `\x08__bunstr_NNNN` for strings
- The `SPECIAL_CHARS` table determines which characters get escaped in shell strings
- The `jsobjs` array holds JavaScript object references passed to the shell

Write tests to verify that strings containing the sentinel byte round-trip correctly, out-of-bounds references are handled safely, and the shell operates without crashes or lex errors.
