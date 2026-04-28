# Bug: Excessive lru_cache warnings when using einops with torch.compile

## Problem

When tracing einops operations through `torch.compile`, Dynamo produces excessive warning spam about `@lru_cache` usage. Every single einops operation triggers a warning because einops internally uses `@lru_cache` in its transformation recipe preparation, and Dynamo does not trace into `@lru_cache` decorated functions.

## Expected Behavior

Compiled einops operations should execute without producing `lru_cache` warnings. The function `_allow_in_graph_einops` is responsible for registering einops functions via `allow_in_graph` so that Dynamo treats them as opaque and does not attempt to trace into them.

However, `allow_in_graph` is never actually called for einops functions, and the warning spam persists.

## Requirements

The function `_allow_in_graph_einops` must:

1. Import the `einops` module
2. Call `allow_in_graph` on einops functions so Dynamo handles them correctly
3. Register at least 4 of the following 6 einops functions: `rearrange`, `reduce`, `repeat`, `einsum`, `pack`, `unpack`
4. Have a substantive implementation body (at least 4 AST statements — not just `pass` or `return None`)

## Symptom

Calling `torch.compile` on code that uses einops operations (such as `rearrange` or `reduce`) produces `lru_cache` warning spam. The `_allow_in_graph_einops` function exists but fails to actually register the einops functions with `allow_in_graph`. Fix the function so that registration always occurs for the required einops operations.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff check` (error-level rules: E9, F63, F7, F82)
