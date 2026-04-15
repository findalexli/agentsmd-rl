# Bun shell braces panic on empty string

## Problem

When `Bun.$.braces("")` is called with an empty string, the Bun runtime crashes
with an index-out-of-bounds panic. This happens in `src/shell/braces.zig`.

## Root Causes

1. `flattenTokens()` — The tokenizer produces zero tokens for empty input, but
   `flattenTokens()` unconditionally accesses `self.tokens.items[0]` without
   checking if the token list is empty first. An early return when the token
   list is empty prevents this.

2. `Parser.advance()` — This function calls `prev()` which performs
   `self.current - 1` on a `usize`. When `current == 0`, this underflows.
   The guard must prevent calling `prev()` when `current == 0`.

## Symptom

- `Bun.$.braces("")` panics with index-out-of-bounds in `flattenTokens`
- `Bun.$.braces("")` panics with underflow wraparound in `advance()`

## Expected Behavior

Calling `$.braces("")` with an empty string must return without crashing.
The return value when input is empty is an empty expansion list
(`[""]` for the default call, `""` for `{parse: true}`, `""` for
`{tokenize: true}`).

## Files to Look At

- `src/shell/braces.zig` — The shell brace expansion implementation
  - `flattenTokens()` function — must handle empty token list gracefully
  - `Parser.advance()` function — must prevent usize underflow in its `prev()` call

## Constraints on the Solution

Both guards must be implemented in `src/shell/braces.zig`:

1. `flattenTokens()` must guard the empty token case. The guard expression must
   contain the substring `self.tokens.items.len == 0` (e.g.
   `if (self.tokens.items.len == 0) return;` or equivalent).

2. `Parser.advance()` must guard the `prev()` call against underflow when
   `current == 0`. The guard must use the pattern `self.current > 0` with a
   fallback to `self.peek()` — the exact string `if (self.current > 0) self.prev() else self.peek()`
   must be present in the function.

## Notes

- The Bun codebase forbids `unreachable` — use proper error handling or
  conditional guards instead.
- All shell-related Zig files must pass `zig fmt --check` and `zig ast-check`.
- A regression test for the empty string case should be added to
  `test/js/bun/shell/brace.test.ts` using `$.braces('')`.