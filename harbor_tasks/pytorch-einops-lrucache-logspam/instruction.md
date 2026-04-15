# Bug: Excessive lru_cache warnings when using einops with torch.compile

## Problem

When tracing einops operations through `torch.compile`, Dynamo produces excessive warning spam about `@lru_cache` usage. Every single einops operation triggers a warning because einops internally uses `@lru_cache` in its transformation recipe preparation, and Dynamo does not trace into `@lru_cache` decorated functions.

## Expected Behavior

Compiled einops operations should execute without producing `lru_cache` warnings. The integration mechanism should ensure all core einops functions are properly registered so Dynamo treats them as opaque.

## Constraints

The fix must be made in `torch/_dynamo/decorators.py` in a function that:
- Imports the `einops` module
- Registers the following einops functions via `allow_in_graph`: `rearrange`, `reduce`, `repeat`, `einsum`, `pack`, `unpack` (at least 4 of these 6 must be registered)
- Contains at least 4 substantive AST statements (not just `pass` or `return None`)
- Handles the einops 0.8.2 version string (the string `"0.8.2"` will appear in the code)

## Symptom

With the current code, einops 0.8.2 triggers an early-return path that bypasses the registration mechanism entirely, causing every einops operation to produce `lru_cache` warning spam during compilation.
