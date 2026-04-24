# Harden Shell Interpolation and Object Reference Validation

## Problem

Bun's shell implementation uses an internal sentinel byte (`0x08`, backspace character) to mark JavaScript object and string references in shell command templates. When user-supplied strings containing this sentinel byte are passed to shell commands, the implementation fails to properly handle them.

## Symptoms

1. Passing strings containing the sentinel byte (0x08) followed by `__bun_` or `__bunstr_` prefixes to shell interpolation causes lex errors
2. Using raw sentinel patterns with certain index values causes crashes instead of graceful errors
3. Shell commands with certain string arguments fail unexpectedly

The sentinel byte is `0x08` (the backspace/BS character). Internal reference patterns use this sentinel:
- `\x08__bun_NNNN` — marks a JS object reference (where NNNN is a decimal index)
- `\x08__bunstr_NNNN` — marks a JS string reference

## Expected Behavior

- Strings containing the sentinel byte (including user strings that accidentally contain `\x08__bun_` or `\x08__bunstr_` patterns) should round-trip through shell interpolation without causing lex errors
- Out-of-bounds object reference indices (e.g., a reference to index 99999 when only a few objects exist) must throw the error: `Invalid JS object reference in shell` instead of crashing
- Stdio redirections should use the correct file descriptor indices

## Required Implementation Details

The following specific identifiers and patterns must be present in the implementation (the agent must discover these through code analysis, not guess them):

### Lexer bounds checking
- `src/shell/shell.zig` — The `Lexer` struct and its `new()` function must include a `jsobjs_len: u32` field/parameter for bounds validation
- The bounds checking logic must compare against `jsobjs_len` (not `maxInt(u32)`)

### Interpolation handling
- `src/shell/interpreter.zig` — Must calculate `jsobjs_len` from the `jsobjs` array length and pass it to the lexer
- The lexer must receive `jsobjs_len` as an argument when instantiated

### Validation function
- `src/shell/shell.zig` — The `validateJSObjRefIdx` function must check indices against the actual object count (`jsobjs_len`), not an unbounded maximum

### Redirection bounds checks
- `src/shell/Builtin.zig` — Must validate `idx >= interpreter.jsobjs.len` (or similar with `jsbuf.idx` / `file.jsbuf.idx`) in `initRedirections`
- `src/shell/states/Cmd.zig` — Must validate `val.idx >= this.base.interpreter.jsobjs.len` (or similar) in `initRedirections`

## Files to Modify

The relevant source files are in `src/shell/`:
- `src/shell/shell.zig` — Shell lexer implementation
- `src/shell/interpreter.zig` — Shell interpreter
- `src/shell/states/Cmd.zig` — Command state handling
- `src/shell/Builtin.zig` — Builtin command handling

## Technical Context

The lexer must be able to handle user strings that accidentally contain sentinel patterns without causing lexer failures. When a JS object is interpolated into a shell command, the lexer converts it to a sentinel-byte reference. If the user's string already contains `\x08__bun_NNNN` pattern (for some other reason), the lexer must not misinterpret it as a JS object reference.

The fix requires:
1. The lexer to know how many JS objects will be referenced (so it can properly validate index bounds)
2. Bounds checks on object reference indices that throw a JavaScript error rather than panicking
3. Proper handling of `jsbuf` fields in redirection code paths

## Validation Required

Write tests to verify:
1. Strings containing the sentinel byte (0x08) round-trip correctly through shell interpolation — specifically strings containing `\x08__bun_NNNN` or `\x08__bunstr_NNNN` patterns that are NOT actual JS references
2. Out-of-bounds JS object reference indices (large numbers like 99999 when only a few objects exist) throw error: `Invalid JS object reference in shell`
3. Shell operates without crashes or lex errors when processing such strings

## Implementation Notes

- The lexer needs to know the number of JS object references for proper bounds checking
- Redirection handling must use correct file descriptor indices
- Builtin commands and Cmd state must validate object reference indices before accessing `interpreter.jsobjs`
- The error message `Invalid JS object reference in shell` must be thrown (not a panic) for out-of-bounds references