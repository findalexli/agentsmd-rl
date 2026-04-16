# Harden Shell Interpolation and Object Reference Validation

## Problem

Bun's shell implementation uses an internal sentinel byte (`0x08`, backspace character) to mark JavaScript object and string references in shell command templates. When user-supplied strings containing this sentinel byte are passed to shell commands, the implementation fails to properly handle them.

## Symptoms

1. Passing strings containing the sentinel byte followed by `__bun_` or `__bunstr_` prefixes to shell interpolation causes lex errors
2. Using raw sentinel patterns with certain index values causes crashes instead of graceful errors
3. Shell commands with certain string arguments fail unexpectedly

## Expected Behavior

- Strings containing the sentinel byte should round-trip through shell interpolation correctly
- Out-of-bounds object references should throw error: `Invalid JS object reference in shell`
- Stdio redirections should use the correct file descriptor indices

## Files to Modify

The relevant source files are in `src/shell/`:
- `src/shell/shell.zig` — Shell lexer implementation
- `src/shell/interpreter.zig` — Shell interpreter
- `src/shell/states/Cmd.zig` — Command state handling
- `src/shell/Builtin.zig` — Builtin command handling

## Technical Context

The sentinel byte is `0x08` (backspace character). The internal reference patterns are:
- `\x08__bun_NNNN` for object references
- `\x08__bunstr_NNNN` for string references

The lexer must be able to handle user strings that accidentally contain these patterns without causing lex failures.

## Validation Required

Write tests to verify:
1. Strings containing the sentinel byte round-trip correctly through shell interpolation
2. Out-of-bounds references are caught and throw a JavaScript error
3. Shell operates without crashes or lex errors when processing such strings

## Implementation Notes

- The lexer needs to know the number of JS object references for proper bounds checking
- Redirection handling must use correct file descriptor indices
- Builtin commands and Cmd state must validate object reference indices before use