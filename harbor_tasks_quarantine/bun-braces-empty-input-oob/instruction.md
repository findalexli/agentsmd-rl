# Bug: `Bun.$.braces("")` panics on empty string input

## Description

Calling `Bun.$.braces("")` with an empty string causes a runtime panic. The shell's brace expansion lexer in `src/shell/braces.zig` does not handle the case where tokenization produces zero tokens.

The parser unconditionally accesses the first token without checking if the token list is empty, and also performs a subtraction that underflows when the position counter is at zero.

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

- `src/shell/braces.zig` — the brace expansion lexer and parser

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
