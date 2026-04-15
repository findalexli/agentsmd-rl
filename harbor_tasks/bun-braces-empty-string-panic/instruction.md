# Bun shell braces panic on empty string

## Problem

When `Bun.$.braces("")` is called with an empty string, the Bun runtime crashes
with an index-out-of-bounds panic followed by an integer underflow panic.

## Symptom

Calling `$.braces("")` with an empty string causes the Bun runtime to panic.
The crash occurs in the brace expansion code at `src/shell/braces.zig`.

The panic manifests as:
- Index out of bounds when the code attempts to access the first element of a token list
- Integer underflow (usize) when decrementing a counter that is already at zero

## Expected Behavior

Calling `$.braces("")` with an empty string must return without crashing.
The return value when input is empty is an empty expansion list:
- `[""]` for the default call `$.braces("")`
- `""` for `$.braces("", {parse: true})`
- `""` for `$.braces("", {tokenize: true})`

## Requirements

1. All fixes must be in `src/shell/braces.zig`.
2. The code must handle the case where tokenizing an empty string produces no tokens.
3. The code must handle state transitions without causing integer underflow on usize counters.
4. All shell-related Zig files must pass `zig fmt --check` and `zig ast-check`.
5. A regression test for the empty string case must be added to
   `test/js/bun/shell/brace.test.ts` calling `$.braces("")`.
