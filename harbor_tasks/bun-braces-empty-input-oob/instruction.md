# Bug: `Bun.$.braces("")` panics on empty string input

## Description

Calling `Bun.$.braces("")` with an empty string causes a runtime panic. The shell's brace expansion lexer in `src/shell/braces.zig` does not handle the case where tokenization produces zero tokens.

There are two crash sites:

1. **`flattenTokens`** — After tokenizing an empty string, the token list is empty. The function unconditionally accesses the first element of the token list (`self.tokens.items[0]`) without checking whether the list has any items. This causes an index-out-of-bounds panic.

2. **`Parser.advance()`** — When the parser's current position is at 0 (as it is at the start with zero tokens), the `advance()` method calls `prev()`, which attempts to access `self.current - 1`. Since `current` is a `u32` starting at 0, this subtraction underflows and causes another panic.

## Reproducer

```js
// All three of these crash:
Bun.$.braces("");
Bun.$.braces("", { parse: true });
Bun.$.braces("", { tokenize: true });
```

## Expected Behavior

`Bun.$.braces("")` should return `[""]` without crashing. The `parse: true` and `tokenize: true` variants should also handle empty input gracefully.

## Files to Investigate

- `src/shell/braces.zig` — specifically the `flattenTokens` function and the `Parser.advance()` method
