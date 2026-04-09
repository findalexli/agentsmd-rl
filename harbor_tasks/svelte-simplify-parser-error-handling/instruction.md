# Simplify parser error handling

## Problem

The Svelte compiler's parser has a fragmented error handling pattern. When acorn (the JavaScript parser) encounters a syntax error, the error conversion logic is scattered across multiple call sites:

- `parse_expression_at()` in `acorn.js` does not catch errors at all — it lets raw acorn `SyntaxError` exceptions propagate to callers
- Each caller (`context.js`, `expression.js`, `script.js`) independently wraps calls in try/catch and converts errors via `parser.acorn_error()`
- The `Parser` class in `index.js` carries an `acorn_error()` method and a `regex_position_indicator` regex that logically belong with the parsing utilities in `acorn.js`
- The `parse()` function handles its result (`add_comments`, return) outside the try block, after the finally

This scattered pattern means every new call site for `parse_expression_at` must remember to wrap it in try/catch and call `parser.acorn_error` — easy to forget and error-prone.

## Expected Behavior

Error handling for acorn parse failures should be centralized in `acorn.js` so that:

1. `parse_expression_at()` and `parse()` handle their own errors internally
2. Callers don't need redundant try/catch blocks just to convert acorn errors
3. The error conversion logic (stripping position indicators, calling `js_parse_error`) lives in one place
4. The `Parser` class is simplified — it should not carry parse-error conversion responsibility

## Files to Look At

- `packages/svelte/src/compiler/phases/1-parse/acorn.js` — Core parsing utilities, `parse()` and `parse_expression_at()`
- `packages/svelte/src/compiler/phases/1-parse/index.js` — `Parser` class definition
- `packages/svelte/src/compiler/phases/1-parse/read/context.js` — `read_pattern()` calls `parse_expression_at`
- `packages/svelte/src/compiler/phases/1-parse/read/expression.js` — `read_expression()` calls `parse_expression_at`
- `packages/svelte/src/compiler/phases/1-parse/read/script.js` — `read_script()` calls `parse()`
