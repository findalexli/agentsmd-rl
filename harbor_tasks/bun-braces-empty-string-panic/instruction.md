# Bun shell braces panic on empty string

## Problem

When `Bun.$.braces("")` is called with an empty string, the Bun runtime crashes with an index-out-of-bounds panic. This happens in `src/shell/braces.zig` because:

1. The tokenizer produces zero tokens for an empty input
2. `flattenTokens()` unconditionally accesses `self.tokens.items[0]`, causing an index-out-of-bounds panic when the token list is empty
3. `Parser.advance()` calls `prev()` which underflows when `current == 0` (since `current - 1` on `usize` wraps around)

## Expected Behavior

The code should handle empty input gracefully without crashing. The fix requires adding two bounds checks:

1. In `flattenTokens()`: Add an early return when `self.tokens.items.len == 0`
2. In `advance()`: Guard the `prev()` call to prevent underflow when `current == 0`

## Files to Look At

- `src/shell/braces.zig` — The shell brace expansion implementation
  - `flattenTokens()` function — needs empty token guard
  - `Parser.advance()` function — needs underflow guard

## Hints

The fix is two simple guards:
1. `if (self.tokens.items.len == 0) return;` at the start of `flattenTokens()`
2. Change `return self.prev();` to `return if (self.current > 0) self.prev() else self.peek();` in `advance()`

Note: The Bun codebase forbids using `unreachable` - use proper error handling instead.
